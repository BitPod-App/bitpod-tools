import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

ISSUE_KEY_RE = re.compile(r"\b([A-Z]{2,}-\d+)\b")
QA_TOKEN_RE = re.compile(r"QA_RESULT=(PASSED|FAILED)")

REQUIRED_HEADINGS = [
    "Context",
    "Goal",
    "Implementation List",
    "DO NOT list",
    "DoD / Acceptance Criteria",
]


@dataclass
class Action:
    system: str  # linear | github
    kind: str    # set_status | add_label | comment
    target: str
    payload: Dict[str, Any]


@dataclass
class BotConfig:
    dry_run: bool = True
    backlog_status: str = "📂 Backlog"
    ready_status: str = "☑️ Ready"
    in_progress_status: str = "🏗️ In Progress"
    in_review_status: str = "🧪 In Review"
    done_status: str = "✅ Done"
    icebox_status: str = "🧊 Icebox"
    obsolete_status: str = "🪦 Obsolete"

    type_chore: str = "⚙️ Chore"
    blocked_needs_specs: str = "⛔ needs-specs"
    blocked_needs_type: str = "⛔ needs-type"

    qa_not_done: str = "🔶 QA: Not Done"
    qa_passed: str = "🔷 QA: Passed"
    qa_failed: str = "♦️ QA: Failed"

    pm_waiting: str = "✴️ PM: Waiting"
    pm_approved: str = "❇️ PM: Approved"
    pm_rejected: str = "❌ PM: Rejected"


class LinearBotEngine:
    def __init__(self, config: Optional[BotConfig] = None) -> None:
        self.cfg = config or BotConfig()

    def find_issue_key(self, text: str) -> Optional[str]:
        if not text:
            return None
        m = ISSUE_KEY_RE.search(text)
        return m.group(1) if m else None

    def has_required_headings(self, description: str) -> bool:
        if not description:
            return False
        return all(h.lower() in description.lower() for h in REQUIRED_HEADINGS)

    def _issue_linking_comment(self) -> str:
        return "Missing Linear issue key; cannot automate."

    def on_github_pr_opened(self, event: Dict[str, Any]) -> List[Action]:
        pr = event.get("pull_request", {})
        issue_key = (
            self.find_issue_key(pr.get("title", ""))
            or self.find_issue_key(pr.get("body", ""))
            or self.find_issue_key(pr.get("head", {}).get("ref", ""))
        )
        if not issue_key:
            return [
                Action(
                    system="github",
                    kind="comment",
                    target=str(pr.get("number", "")),
                    payload={"body": self._issue_linking_comment()},
                )
            ]

        return [
            Action("linear", "set_status", issue_key, {"status": self.cfg.in_progress_status}),
            Action("linear", "comment", issue_key, {"body": f"PR opened: {pr.get('html_url', '')}"}),
        ]

    def on_github_pr_ready_for_review(self, event: Dict[str, Any]) -> List[Action]:
        pr = event.get("pull_request", {})
        issue_key = (
            self.find_issue_key(pr.get("title", ""))
            or self.find_issue_key(pr.get("body", ""))
            or self.find_issue_key(pr.get("head", {}).get("ref", ""))
        )
        if not issue_key:
            return [Action("github", "comment", str(pr.get("number", "")), {"body": self._issue_linking_comment()})]

        return [
            Action("linear", "set_status", issue_key, {"status": self.cfg.in_review_status}),
            Action("linear", "set_label", issue_key, {"group": "🧪 QA", "value": self.cfg.qa_not_done}),
            Action("linear", "set_label_if_empty", issue_key, {"group": "🔑 PM", "value": self.cfg.pm_waiting}),
            Action("linear", "comment", issue_key, {"body": f"PR in review: {pr.get('html_url', '')}. QA set to Not Done."}),
        ]

    def on_linear_ready_gate(self, issue: Dict[str, Any]) -> List[Action]:
        issue_key = issue.get("identifier", "")
        if issue.get("status") != self.cfg.ready_status:
            return []

        labels = set(issue.get("labels", []))
        description = issue.get("description", "")

        actions: List[Action] = []
        allowed_types = {"⭐️ Feature", "🐞 Bug", "⚙️ Chore", "🎨 Design", "🏁 Release"}
        if not labels.intersection(allowed_types):
            actions.extend([
                Action("linear", "set_label", issue_key, {"group": "🛑 Blocked", "value": self.cfg.blocked_needs_type}),
                Action("linear", "comment", issue_key, {"body": "Missing `🏷️ Type`. Set one of: `⭐️ Feature` `🐞 Bug` `⚙️ Chore` `🎨 Design` `🏁 Release`"}),
                Action("linear", "set_status", issue_key, {"status": self.cfg.backlog_status}),
            ])
            return actions

        if not self.has_required_headings(description):
            actions.extend([
                Action("linear", "set_label", issue_key, {"group": "🛑 Blocked", "value": self.cfg.blocked_needs_specs}),
                Action("linear", "comment", issue_key, {"body": "Missing required sections: Context / Goal / Implementation List / DO NOT list / DoD / Acceptance Criteria"}),
                Action("linear", "set_status", issue_key, {"status": self.cfg.backlog_status}),
            ])
            return actions

        return actions

    def on_linear_comment(self, issue_key: str, comment_body: str, pr_url: str = "") -> List[Action]:
        m = QA_TOKEN_RE.search(comment_body or "")
        if not m:
            return []

        token = m.group(1)
        summary = "\n".join((comment_body or "").splitlines()[:10])
        if token == "FAILED":
            return [
                Action("linear", "set_label", issue_key, {"group": "🧪 QA", "value": self.cfg.qa_failed}),
                Action("linear", "set_status", issue_key, {"status": self.cfg.in_progress_status}),
                Action("github", "comment", pr_url, {"body": f"QA FAILED. Summary: {summary}"}),
            ]

        return [
            Action("linear", "set_label", issue_key, {"group": "🧪 QA", "value": self.cfg.qa_passed}),
            Action("linear", "set_label", issue_key, {"group": "🔑 PM", "value": self.cfg.pm_waiting}),
            Action("github", "comment", pr_url, {"body": "QA PASSED. Awaiting PM approval in Linear."}),
        ]

    def on_github_pr_merged(self, issue: Dict[str, Any], pr_url: str, merge_sha: str) -> List[Action]:
        issue_key = issue.get("identifier", "")
        labels = set(issue.get("labels", []))
        if self.cfg.qa_passed in labels and self.cfg.pm_approved in labels:
            return [
                Action("linear", "set_status", issue_key, {"status": self.cfg.done_status}),
                Action("linear", "comment", issue_key, {"body": f"Merged: {pr_url} | SHA: {merge_sha}"}),
            ]

        return [
            Action("linear", "comment", issue_key, {"body": "Merged detected but gates not satisfied (need QA Passed + PM Approved). Manual review required."})
        ]

    def daily_aging_scan(self, issues: List[Dict[str, Any]], now: Optional[datetime] = None) -> List[Action]:
        now = now or datetime.now(timezone.utc)
        out: List[Action] = []

        for issue in issues:
            status = issue.get("status", "")
            last_updated = issue.get("updatedAt") or issue.get("lastCommentAt")
            if not last_updated:
                continue
            dt = datetime.fromisoformat(last_updated.replace("Z", "+00:00"))
            idle_days = (now - dt).days
            key = issue.get("identifier", "")

            if status == self.cfg.backlog_status and idle_days >= 30:
                out.append(Action("linear", "set_status", key, {"status": self.cfg.icebox_status}))
                out.append(Action("linear", "comment", key, {"body": "Auto-moved to Icebox after 30d inactivity."}))
            elif status == self.cfg.icebox_status and idle_days >= 60:
                out.append(Action("linear", "set_status", key, {"status": self.cfg.obsolete_status}))
                out.append(Action("linear", "comment", key, {"body": "Auto-closed as Obsolete after 60d inactivity in Icebox."}))

        return out


def format_actions(actions: List[Action]) -> str:
    return json.dumps([a.__dict__ for a in actions], indent=2)
