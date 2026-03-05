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
    kind: str
    target: str
    payload: Dict[str, Any]


@dataclass
class BotConfig:
    dry_run: bool = True

    # desired v1 statuses from SOP
    backlog_status: str = "📂 Backlog"
    ready_status: str = "☑️ Ready"
    in_progress_status: str = "🏗️ In Progress"
    in_review_status: str = "🧪 In Review"
    done_status: str = "✅ Done"
    icebox_status: str = "🧊 Icebox"
    obsolete_status: str = "🪦 Obsolete"

    # fallback current BIT statuses (transitional)
    fallback_backlog_status: str = "Backlog"
    fallback_in_progress_status: str = "In Progress"
    fallback_in_review_status: str = "In Review"
    fallback_done_status: str = "Done"
    fallback_icebox_status: str = "Icebox 🧊"
    fallback_obsolete_status: str = "Obsolete"

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

    def _status(self, primary: str, fallback: str) -> str:
        """Use primary SOP status by default; can be swapped by deploy-time config later."""
        return primary or fallback

    def _backlog(self) -> str:
        return self._status(self.cfg.backlog_status, self.cfg.fallback_backlog_status)

    def _in_progress(self) -> str:
        return self._status(self.cfg.in_progress_status, self.cfg.fallback_in_progress_status)

    def _in_review(self) -> str:
        return self._status(self.cfg.in_review_status, self.cfg.fallback_in_review_status)

    def _done(self) -> str:
        return self._status(self.cfg.done_status, self.cfg.fallback_done_status)

    def _icebox(self) -> str:
        return self._status(self.cfg.icebox_status, self.cfg.fallback_icebox_status)

    def _obsolete(self) -> str:
        return self._status(self.cfg.obsolete_status, self.cfg.fallback_obsolete_status)

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

    def on_github_pr_opened(self, event: Dict[str, Any]) -> List[Action]:
        pr = event.get("pull_request", {})
        issue_key = self._linked_issue_from_pr(pr)
        if not issue_key:
            return [
                Action("github", "comment", str(pr.get("number", "")), {"body": self._issue_linking_comment()})
            ]

        return [
            Action("linear", "set_status", issue_key, {"status": self._in_progress()}),
            Action("linear", "comment", issue_key, {"body": f"PR opened: {pr.get('html_url', '')}"}),
        ]

    def on_github_pr_ready_for_review(self, event: Dict[str, Any]) -> List[Action]:
        pr = event.get("pull_request", {})
        issue_key = self._linked_issue_from_pr(pr)
        if not issue_key:
            return [Action("github", "comment", str(pr.get("number", "")), {"body": self._issue_linking_comment()})]

        return [
            Action("linear", "set_status", issue_key, {"status": self._in_review()}),
            Action("linear", "set_label", issue_key, {"group": "🧪 QA", "value": self.cfg.qa_not_done}),
            Action("linear", "set_label_if_empty", issue_key, {"group": "🔑 PM", "value": self.cfg.pm_waiting}),
            Action("linear", "comment", issue_key, {"body": f"PR in review: {pr.get('html_url', '')}. QA set to Not Done."}),
        ]

    def on_linear_ready_gate(self, issue: Dict[str, Any]) -> List[Action]:
        issue_key = issue.get("identifier", "")
        status_name = issue.get("status", "")
        if status_name != self.cfg.ready_status:
            return []

        labels = set(issue.get("labels", []))
        description = issue.get("description", "")

        allowed_types = {"⭐️ Feature", "🐞 Bug", "⚙️ Chore", "🎨 Design", "🏁 Release", "⚙️ Chore"}
        if not labels.intersection(allowed_types):
            return [
                Action("linear", "set_label", issue_key, {"group": "🛑 Blocked", "value": self.cfg.blocked_needs_type}),
                Action("linear", "comment", issue_key, {"body": "Missing `🏷️ Type`. Set one of: `⭐️ Feature` `🐞 Bug` `⚙️ Chore` `🎨 Design` `🏁 Release`"}),
                Action("linear", "set_status", issue_key, {"status": self._backlog()}),
            ]

        if not self.has_required_headings(description):
            return [
                Action("linear", "set_label", issue_key, {"group": "🛑 Blocked", "value": self.cfg.blocked_needs_specs}),
                Action("linear", "comment", issue_key, {"body": "Missing required sections: Context / Goal / Implementation List / DO NOT list / DoD / Acceptance Criteria"}),
                Action("linear", "set_status", issue_key, {"status": self._backlog()}),
            ]

        return []

    def on_linear_comment(self, issue_key: str, comment_body: str, pr_url: str = "") -> List[Action]:
        m = QA_TOKEN_RE.search(comment_body or "")
        if not m:
            return []

        token = m.group(1)
        summary = "\n".join((comment_body or "").splitlines()[:10])
        if token == "FAILED":
            return [
                Action("linear", "set_label", issue_key, {"group": "🧪 QA", "value": self.cfg.qa_failed}),
                Action("linear", "set_status", issue_key, {"status": self._in_progress()}),
                Action("github", "comment", pr_url, {"body": f"QA FAILED. Summary: {summary}. See Linear: {issue_key}"}),
            ]

        return [
            Action("linear", "set_label", issue_key, {"group": "🧪 QA", "value": self.cfg.qa_passed}),
            Action("linear", "set_label", issue_key, {"group": "🔑 PM", "value": self.cfg.pm_waiting}),
            Action("github", "comment", pr_url, {"body": f"QA PASSED. Awaiting PM approval in Linear. {issue_key}"}),
        ]

    def on_linear_pm_label_change(self, issue_key: str, pm_value: str, pr_url: str = "") -> List[Action]:
        if pm_value == self.cfg.pm_rejected:
            return [
                Action("linear", "set_status", issue_key, {"status": self._in_progress()}),
                Action("github", "comment", pr_url, {"body": f"PM REJECTED. See Linear for notes: {issue_key}"}),
            ]
        if pm_value == self.cfg.pm_approved:
            return [
                Action("github", "comment", pr_url, {"body": "PM APPROVED. Merge authorized. (Bot will close issue after merge if QA Passed.)"})
            ]
        return []

    def on_github_pr_merged(self, issue: Dict[str, Any], pr_url: str, merge_sha: str) -> List[Action]:
        issue_key = issue.get("identifier", "")
        labels = set(issue.get("labels", []))
        if self.cfg.qa_passed in labels and self.cfg.pm_approved in labels:
            return [
                Action("linear", "set_status", issue_key, {"status": self._done()}),
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

            if status in (self.cfg.backlog_status, self.cfg.fallback_backlog_status) and idle_days >= 30:
                out.append(Action("linear", "set_status", key, {"status": self._icebox()}))
                out.append(Action("linear", "comment", key, {"body": "Auto-moved to Icebox after 30d inactivity."}))
            elif status in (self.cfg.icebox_status, self.cfg.fallback_icebox_status) and idle_days >= 60:
                out.append(Action("linear", "set_status", key, {"status": self._obsolete()}))
                out.append(Action("linear", "comment", key, {"body": "Auto-closed as Obsolete after 60d inactivity in Icebox."}))

        return out


def format_actions(actions: List[Action]) -> str:
    return json.dumps([a.__dict__ for a in actions], indent=2)
