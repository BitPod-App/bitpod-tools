#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from linear.src.engine import BotConfig, LinearBotEngine


API_URL = "https://api.linear.app/graphql"
DEFAULT_TEAM = "Product Development"


@dataclass
class QueueEntry:
    identifier: str
    title: str
    url: str
    status: str
    queue: str
    assignee: str
    project: str
    labels: List[str]
    blockers: List[str]
    updated_at: str


def _auth_header(token: str) -> str:
    token = (token or "").strip()
    if not token:
        raise SystemExit("LINEAR_API_KEY is required for live fetches.")
    if token.lower().startswith("bearer "):
        return token
    return f"Bearer {token}"


def gql_request(token: str, query: str, variables: Dict[str, Any]) -> Dict[str, Any]:
    req = urllib.request.Request(
        API_URL,
        data=json.dumps({"query": query, "variables": variables}).encode("utf-8"),
        headers={
            "Authorization": _auth_header(token),
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req) as response:
        payload = json.loads(response.read().decode("utf-8"))
    if payload.get("errors"):
        raise SystemExit(json.dumps(payload["errors"], indent=2))
    return payload


def fetch_all_issues(token: str, page_size: int = 250) -> List[Dict[str, Any]]:
    query = """
    query IssuesPage($first: Int!, $after: String) {
      issues(first: $first, after: $after) {
        nodes {
          identifier
          title
          url
          updatedAt
          state {
            name
          }
          assignee {
            name
          }
          project {
            name
          }
          team {
            name
          }
          labels {
            nodes {
              name
            }
          }
        }
        pageInfo {
          hasNextPage
          endCursor
        }
      }
    }
    """
    issues: List[Dict[str, Any]] = []
    cursor: Optional[str] = None
    while True:
        payload = gql_request(token, query, {"first": page_size, "after": cursor})
        page = payload.get("data", {}).get("issues", {})
        issues.extend(page.get("nodes", []))
        info = page.get("pageInfo", {})
        if not info.get("hasNextPage"):
            return issues
        cursor = info.get("endCursor")
        if not cursor:
            return issues


def load_issues(input_json: str) -> List[Dict[str, Any]]:
    with open(input_json, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if isinstance(payload, dict) and "issues" in payload:
        issues = payload["issues"]
    else:
        issues = payload
    if not isinstance(issues, list):
        raise SystemExit(f"invalid issues payload: {input_json}")
    return issues


def issue_status(issue: Dict[str, Any]) -> str:
    state = issue.get("state")
    if isinstance(state, dict):
        return str(state.get("name", "") or "")
    return str(issue.get("status", "") or "")


def issue_labels(issue: Dict[str, Any]) -> List[str]:
    labels = issue.get("labels", [])
    if isinstance(labels, dict):
        labels = labels.get("nodes", [])
    out: List[str] = []
    for label in labels or []:
        if isinstance(label, dict):
            name = label.get("name")
        else:
            name = label
        if name:
            out.append(str(name))
    return sorted(set(out))


def issue_team(issue: Dict[str, Any]) -> str:
    team = issue.get("team")
    if isinstance(team, dict):
        return str(team.get("name", "") or "")
    return str(team or "")


def issue_project(issue: Dict[str, Any]) -> str:
    project = issue.get("project")
    if isinstance(project, dict):
        return str(project.get("name", "") or "")
    return str(project or "")


def issue_assignee(issue: Dict[str, Any]) -> str:
    assignee = issue.get("assignee")
    if isinstance(assignee, dict):
        return str(assignee.get("name", "") or "")
    return str(assignee or "")


def _push_unique(items: List[str], value: str) -> None:
    if value and value not in items:
        items.append(value)


def scan_issue(
    issue: Dict[str, Any],
    *,
    cfg: Optional[BotConfig] = None,
    bot: Optional[LinearBotEngine] = None,
    include_accepted: bool = False,
) -> Optional[QueueEntry]:
    cfg = cfg or BotConfig()
    bot = bot or LinearBotEngine(cfg)
    status = issue_status(issue)
    labels = issue_labels(issue)
    label_set = set(labels)

    if status == cfg.in_review_status:
        queue = "QA"
    elif status == cfg.delivered_status:
        queue = "PM"
    elif include_accepted and status == cfg.accepted_status:
        queue = "Accepted"
    else:
        return None

    blockers: List[str] = []
    if cfg.qa_failed in label_set:
        _push_unique(blockers, cfg.qa_failed)
    if cfg.qa_skipped in label_set:
        _push_unique(blockers, cfg.qa_skipped)
    elif cfg.qa_passed not in label_set:
        _push_unique(blockers, f"missing {cfg.qa_passed}")

    if status in {cfg.delivered_status, cfg.accepted_status}:
        if cfg.pm_rejected in label_set:
            _push_unique(blockers, cfg.pm_rejected)
        elif cfg.pm_accepted not in label_set:
            _push_unique(blockers, f"missing {cfg.pm_accepted}")

    if bot._has_blocker_signal(issue, set(labels)):
        if cfg.blocked_label in label_set:
            _push_unique(blockers, cfg.blocked_label)
        for label in labels:
            if label.startswith("needs-"):
                _push_unique(blockers, label)

    return QueueEntry(
        identifier=str(issue.get("identifier", "")),
        title=str(issue.get("title", "")),
        url=str(issue.get("url", "")),
        status=status,
        queue=queue,
        assignee=issue_assignee(issue) or "unassigned",
        project=issue_project(issue) or "no project",
        labels=labels,
        blockers=blockers,
        updated_at=str(issue.get("updatedAt", "") or ""),
    )


def build_queue(
    issues: Sequence[Dict[str, Any]],
    *,
    team: str,
    project: str = "",
    include_accepted: bool = False,
    cfg: Optional[BotConfig] = None,
) -> List[QueueEntry]:
    cfg = cfg or BotConfig()
    bot = LinearBotEngine(cfg)
    entries: List[QueueEntry] = []
    for issue in issues:
        if issue_team(issue) != team:
            continue
        if project and issue_project(issue) != project:
            continue
        entry = scan_issue(issue, cfg=cfg, bot=bot, include_accepted=include_accepted)
        if entry:
            entries.append(entry)
    entries.sort(key=lambda item: (item.queue, item.identifier))
    return entries


def summarize_blockers(entries: Iterable[QueueEntry]) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for entry in entries:
        for blocker in entry.blockers:
            counts[blocker] = counts.get(blocker, 0) + 1
    return dict(sorted(counts.items(), key=lambda item: (-item[1], item[0])))


def render_report(
    entries: Sequence[QueueEntry],
    *,
    team: str,
    project: str = "",
    source: str,
) -> str:
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    lines = [
        "BIT handoff queue report",
        f"generated_at: {now}",
        f"team: {team}",
        f"source: {source}",
    ]
    if project:
        lines.append(f"project: {project}")

    if not entries:
        lines.extend(["", "No live QA/PM gate blockers found in the tracked handoff states."])
        return "\n".join(lines)

    lines.append("")
    by_queue: Dict[str, List[QueueEntry]] = {"QA": [], "PM": [], "Accepted": []}
    for entry in entries:
        by_queue.setdefault(entry.queue, []).append(entry)

    lines.append("Summary")
    for queue_name in ("QA", "PM", "Accepted"):
        queue_entries = by_queue.get(queue_name, [])
        if not queue_entries:
            continue
        states = sorted({entry.status for entry in queue_entries})
        blockers = summarize_blockers(queue_entries)
        lines.append(f"- {queue_name} queue ({', '.join(states)}): {len(queue_entries)} ticket(s)")
        for blocker, count in blockers.items():
            lines.append(f"  - {count} × {blocker}")

    for queue_name in ("QA", "PM", "Accepted"):
        queue_entries = by_queue.get(queue_name, [])
        if not queue_entries:
            continue
        lines.extend(["", f"{queue_name} queue"])
        for entry in queue_entries:
            blocker_text = ", ".join(entry.blockers) if entry.blockers else "no blockers"
            lines.append(
                f"- {entry.identifier} [{entry.status}] — {blocker_text} — {entry.assignee} — {entry.title}"
            )
            lines.append(f"  {entry.project} | {entry.url}")

    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="Compact visible report for the BIT handoff QA/PM queue.")
    ap.add_argument("--team", default=DEFAULT_TEAM, help="Linear team name. Defaults to Product Development.")
    ap.add_argument("--project", default="", help="Optional project-name filter.")
    ap.add_argument(
        "--include-accepted",
        action="store_true",
        help="Include Accepted tickets that still carry handoff-label debt.",
    )
    ap.add_argument(
        "--input-json",
        default="",
        help="Optional JSON file with an issue list for offline/dev use instead of a live Linear fetch.",
    )
    args = ap.parse_args()

    if args.input_json:
        issues = load_issues(args.input_json)
        source = f"file:{args.input_json}"
    else:
        token = os.environ.get("LINEAR_API_KEY", "")
        issues = fetch_all_issues(token)
        source = "live-linear-api"

    entries = build_queue(
        issues,
        team=args.team,
        project=args.project,
        include_accepted=args.include_accepted,
    )
    print(render_report(entries, team=args.team, project=args.project, source=source))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
