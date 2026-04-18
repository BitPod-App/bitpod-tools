import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set

ISSUE_KEY_RE = re.compile(r"\b([A-Z]{2,}-\d+)\b")
QA_TOKEN_RE = re.compile(r"QA_RESULT=(PASSED|FAILED|SKIPPED)")
PR_URL_TOKEN_RE = re.compile(r"PR_URL=(https?://[^\s]+)")

REQUIRED_HEADINGS = [
    "Objective",
    "Scope",
    "Required outputs",
    "Verification plan",
    "Rollback note",
    "Acceptance / closure criteria",
]

CANONICAL_TYPES = {"Plan", "Feature", "Bug", "Chore", "Design", "Release"}
TYPE_LABEL_ALIASES = {
    "📄 Plan": "Plan",
    "⭐️ Feature": "Feature",
    "🐞 Bug": "Bug",
    "⚙️ Chore": "Chore",
    "🎨 Design": "Design",
    "🏁 Release": "Release",
}
VALID_ESTIMATES = {1, 2, 3, 5, 8}


@dataclass
class Action:
    system: str  # linear | github
    kind: str
    target: str
    payload: Dict[str, Any]


@dataclass
class BotConfig:
    dry_run: bool = True

    backlog_status: str = "Backlog"
    todo_status: str = "Ready"
    in_progress_status: str = "In Progress"
    in_review_status: str = "In Review"
    delivered_status: str = "Delivered"
    accepted_status: str = "Accepted"
    done_status: str = "Done"
    icebox_status: str = "Icebox 🧊"
    stale_status: str = "Stale"
    obsolete_status: str = "Obsolete"

    type_group: str = "Issue Type"
    blocked_group: str = "Blocked By"
    blocked_label: str = "blocked"
    qa_gate_group: str = "QA Review"
    acceptance_gate_group: str = "PM Review"

    blocked_needs_specs: str = "needs-specs"
    blocked_needs_type: str = "needs-type"
    blocked_needs_estimate: str = "needs-estimate"

    qa_passed: str = "qa-passed"
    qa_failed: str = "qa-failed"
    qa_skipped: str = "qa-skipped"

    pm_accepted: str = "pm-accepted"
    pm_rejected: str = "pm-rejected"
    pm_skipped: str = "pm-skipped"


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

    def _linked_issue_from_pr(self, pr: Dict[str, Any]) -> Optional[str]:
        return (
            self.find_issue_key(pr.get("title", ""))
            or self.find_issue_key(pr.get("body", ""))
            or self.find_issue_key(pr.get("head", {}).get("ref", ""))
        )

    def _extract_pr_url_token(self, comment_body: str) -> str:
        m = PR_URL_TOKEN_RE.search(comment_body or "")
        return m.group(1) if m else ""

    def _labels(self, issue_labels: Optional[List[str]]) -> Set[str]:
        return set(issue_labels or [])

    def _normalize_type_label(self, label: str) -> Optional[str]:
        if not label:
            return None
        cleaned = label.strip()
        if cleaned in CANONICAL_TYPES:
            return cleaned
        if cleaned in TYPE_LABEL_ALIASES:
            return TYPE_LABEL_ALIASES[cleaned]
        if cleaned.startswith("Type: "):
            cleaned = cleaned[len("Type: ") :].strip()
            if cleaned in CANONICAL_TYPES:
                return cleaned
            if cleaned in TYPE_LABEL_ALIASES:
                return TYPE_LABEL_ALIASES[cleaned]
        return None

    def _type_labels(self, labels: Set[str]) -> Set[str]:
        return {normalized for label in labels if (normalized := self._normalize_type_label(label))}

    def _is_release(self, labels: Set[str]) -> bool:
        return "Release" in self._type_labels(labels)

    def _has_native_blockers(self, issue: Dict[str, Any]) -> bool:
        candidates = (
            issue.get("blockedBy"),
            issue.get("blocked_by"),
            issue.get("blockingIssues"),
            issue.get("blocking_issues"),
            issue.get("dependencies"),
        )
        for candidate in candidates:
            if candidate:
                return True
        relations = issue.get("relations", {})
        if isinstance(relations, dict) and relations.get("blockedBy"):
            return True
        return False

    def _has_blocker_signal(self, issue: Dict[str, Any], labels: Set[str]) -> bool:
        if self.cfg.blocked_label in labels:
            return True
        if any(label.startswith("needs-") for label in labels):
            return True
        return self._has_native_blockers(issue)

    def _has_valid_estimate(self, issue: Dict[str, Any]) -> bool:
        raw = issue.get("estimate")
        if isinstance(raw, dict):
            raw = raw.get("value")
        if raw in (None, "", 0):
            raw = issue.get("estimateValue")
        try:
            value = int(raw)
        except (TypeError, ValueError):
            return False
        return value in VALID_ESTIMATES

    def _github_comment(self, pr_url: str, body: str) -> List[Action]:
        if not pr_url:
            return []
        return [Action("github", "comment", pr_url, {"body": body})]

    def on_github_pr_opened(self, event: Dict[str, Any]) -> List[Action]:
        pr = event.get("pull_request", {})
        issue_key = self._linked_issue_from_pr(pr)
        if not issue_key:
            return [
                Action("github", "comment", str(pr.get("number", "")), {"body": self._issue_linking_comment()})
            ]

        return [
            Action("linear", "set_status", issue_key, {"status": self.cfg.in_progress_status}),
            Action("linear", "comment", issue_key, {"body": f"PR opened: {pr.get('html_url', '')}"}),
        ]

    def on_github_pr_ready_for_review(self, event: Dict[str, Any]) -> List[Action]:
        pr = event.get("pull_request", {})
        issue_key = self._linked_issue_from_pr(pr)
        if not issue_key:
            return [
                Action("github", "comment", str(pr.get("number", "")), {"body": self._issue_linking_comment()})
            ]

        return [
            Action("linear", "set_status", issue_key, {"status": self.cfg.in_review_status}),
            Action(
                "linear",
                "comment",
                issue_key,
                {"body": f"PR in review: {pr.get('html_url', '')}. The current Product Development review gate is now expressed by `In Review`."},
            ),
        ]

    def on_linear_ready_gate(self, issue: Dict[str, Any]) -> List[Action]:
        issue_key = issue.get("identifier", "")
        status_name = issue.get("status", "")
        if status_name not in (self.cfg.todo_status, self.cfg.in_progress_status):
            return []

        labels = self._labels(issue.get("labels", []))
        description = issue.get("description", "")

        type_labels = self._type_labels(labels)
        if len(type_labels) != 1:
            return [
                Action(
                    "linear",
                    "set_label",
                    issue_key,
                    {"group": self.cfg.blocked_group, "value": self.cfg.blocked_needs_type},
                ),
                Action(
                    "linear",
                    "comment",
                    issue_key,
                    {
                        "body": "Missing or invalid `Issue Type`. Set exactly one canonical type label: `📄 Plan` `⭐️ Feature` `🐞 Bug` `⚙️ Chore` `🎨 Design` `🏁 Release`"
                    },
                ),
                Action("linear", "set_status", issue_key, {"status": self.cfg.backlog_status}),
            ]

        if not self._has_valid_estimate(issue):
            return [
                Action(
                    "linear",
                    "set_label",
                    issue_key,
                    {"group": self.cfg.blocked_group, "value": self.cfg.blocked_needs_estimate},
                ),
                Action(
                    "linear",
                    "comment",
                    issue_key,
                    {"body": "Missing or invalid estimate. Set one of: `1` `2` `3` `5` `8` before moving this issue into active execution."},
                ),
                Action("linear", "set_status", issue_key, {"status": self.cfg.backlog_status}),
            ]

        if not self.has_required_headings(description):
            return [
                Action(
                    "linear",
                    "set_label",
                    issue_key,
                    {"group": self.cfg.blocked_group, "value": self.cfg.blocked_needs_specs},
                ),
                Action(
                    "linear",
                    "comment",
                    issue_key,
                    {
                        "body": "Missing required sections: Objective / Scope / Required outputs / Verification plan / Rollback note / Acceptance / closure criteria"
                    },
                ),
                Action("linear", "set_status", issue_key, {"status": self.cfg.backlog_status}),
            ]

        return []

    def on_linear_comment(
        self,
        issue_key: str,
        comment_body: str,
        pr_url: str = "",
        issue_labels: Optional[List[str]] = None,
        issue_url: str = "",
    ) -> List[Action]:
        m = QA_TOKEN_RE.search(comment_body or "")
        if not m:
            return []

        token = m.group(1)
        labels = self._labels(issue_labels)
        target_pr_url = self._extract_pr_url_token(comment_body) or pr_url
        issue_ref = issue_url or issue_key
        summary = "\n".join((comment_body or "").splitlines()[:10])

        if token == "FAILED":
            actions = [
                Action("linear", "set_label", issue_key, {"group": self.cfg.qa_gate_group, "value": self.cfg.qa_failed}),
                Action("linear", "set_status", issue_key, {"status": self.cfg.in_progress_status}),
            ]
            actions.extend(
                self._github_comment(target_pr_url, f"QA FAILED. Summary: {summary}. See Linear: {issue_ref}")
            )
            return actions

        gate_value = self.cfg.qa_skipped if token == "SKIPPED" else self.cfg.qa_passed
        next_status = self.cfg.delivered_status
        result_text = "QA SKIPPED" if token == "SKIPPED" else "QA PASSED"
        next_text = "Delivered"
        actions = [
            Action("linear", "set_label", issue_key, {"group": self.cfg.qa_gate_group, "value": gate_value}),
            Action("linear", "set_status", issue_key, {"status": next_status}),
        ]
        actions.extend(
            self._github_comment(target_pr_url, f"{result_text}. Linear moved to {next_text}. {issue_ref}")
        )
        return actions

    def on_linear_acceptance_gate_change(
        self,
        issue_key: str,
        gate_value: str,
        pr_url: str = "",
        reason: str = "",
    ) -> List[Action]:
        if gate_value == self.cfg.pm_rejected:
            rejection_reason = reason.strip()
            actions = [
                Action("linear", "set_status", issue_key, {"status": self.cfg.in_progress_status}),
                Action(
                    "linear",
                    "comment",
                    issue_key,
                    {
                        "body": (
                            f"PM rejected; moved back to `In Progress`. Reason: {rejection_reason}"
                            if rejection_reason
                            else "PM rejected; moved back to `In Progress`. Add the rejection reason artifact before resuming work."
                        )
                    },
                ),
            ]
            actions.extend(
                self._github_comment(
                    pr_url,
                    (
                        f"ACCEPTANCE REJECTED. Reason: {rejection_reason}. See Linear: {issue_key}"
                        if rejection_reason
                        else f"ACCEPTANCE REJECTED. Reason required in Linear before resuming work: {issue_key}"
                    ),
                )
            )
            return actions

        if gate_value == self.cfg.pm_accepted:
            actions = [
                Action("linear", "set_status", issue_key, {"status": self.cfg.accepted_status}),
            ]
            actions.extend(
                self._github_comment(pr_url, "ACCEPTANCE APPROVED. Linear status moved to Accepted.")
            )
            return actions

        if gate_value == self.cfg.pm_skipped:
            actions = [
                Action("linear", "set_status", issue_key, {"status": self.cfg.accepted_status}),
            ]
            actions.extend(
                self._github_comment(pr_url, "ACCEPTANCE SKIPPED BY APPROVED OVERRIDE. Linear status moved to Accepted.")
            )
            return actions

        return []

    def on_linear_pm_label_change(self, issue_key: str, pm_value: str, pr_url: str = "") -> List[Action]:
        return self.on_linear_acceptance_gate_change(issue_key, pm_value, pr_url)

    def on_github_pr_merged(self, issue: Dict[str, Any], pr_url: str, merge_sha: str) -> List[Action]:
        issue_key = issue.get("identifier", "")
        labels = self._labels(issue.get("labels", []))
        qa_ok = bool({self.cfg.qa_passed, self.cfg.qa_skipped}.intersection(labels))
        acceptance_ok = bool({self.cfg.pm_accepted, self.cfg.pm_skipped}.intersection(labels))
        status_ok = issue.get("status", "") == self.cfg.accepted_status
        blocked = self._has_blocker_signal(issue, labels)
        release_issue = self._is_release(labels)

        if qa_ok and acceptance_ok and status_ok and not blocked and not release_issue:
            return [
                Action("linear", "set_status", issue_key, {"status": self.cfg.done_status}),
                Action(
                    "linear",
                    "comment",
                    issue_key,
                    {"body": f"Merged recorded: {pr_url} | SHA: {merge_sha}. Linear status moved to `Done` because merge-readiness gates were already satisfied."},
                ),
            ]

        reasons: List[str] = []
        if not qa_ok:
            reasons.append("missing qa-passed/qa-skipped")
        if not acceptance_ok:
            reasons.append("missing pm-accepted/pm-skipped")
        if not status_ok:
            reasons.append("status is not Accepted")
        if blocked:
            reasons.append("issue is blocked by dependencies or blocker labels")
        if release_issue:
            reasons.append("Release issues do not auto-close from normal merge flow")

        return [
            Action(
                "linear",
                "comment",
                issue_key,
                {
                    "body": "Merged detected but Linear closure is blocked: " + "; ".join(reasons) + ". Manual review required."
                },
            )
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
                out.append(
                    Action(
                        "linear",
                        "comment",
                        key,
                        {"body": "Auto-moved from `Backlog` to `Icebox 🧊` after 30d inactivity."},
                    )
                )
            elif status == self.cfg.icebox_status and idle_days >= 30:
                out.append(Action("linear", "set_status", key, {"status": self.cfg.stale_status}))
                out.append(
                    Action(
                        "linear",
                        "comment",
                        key,
                        {
                            "body": "Auto-moved from `Icebox 🧊` to `Stale` after 30d inactivity in `Icebox 🧊`. This ticket can be reopened later if it becomes relevant again."
                        },
                    )
                )

        return out


def format_actions(actions: List[Action]) -> str:
    return json.dumps([a.__dict__ for a in actions], indent=2)
