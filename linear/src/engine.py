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

ACCEPTANCE_REQUIRED_TYPES = {
    "Type: 📄 Plan",
    "Type: 🏁 Release",
    "Type: ⭐️ Feature",
    "Type: 🎨 Design",
}


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
    obsolete_status: str = "Obsolete"

    type_group: str = "Issue Type"
    blocked_group: str = "Blocked By"
    qa_gate_group: str = "QA Gate"
    acceptance_gate_group: str = "Acceptance Gate"

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

    def _requires_acceptance(self, labels: Set[str]) -> bool:
        return bool(labels.intersection(ACCEPTANCE_REQUIRED_TYPES))

    def _has_estimate(self, issue: Dict[str, Any]) -> bool:
        raw = issue.get("estimate")
        if isinstance(raw, dict):
            raw = raw.get("value")
        if raw in (None, "", 0):
            raw = issue.get("estimateValue")
        return raw not in (None, "", 0)

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
                {"body": f"PR in review: {pr.get('html_url', '')}. Pending QA is now expressed by `In Review`."},
            ),
        ]

    def on_linear_ready_gate(self, issue: Dict[str, Any]) -> List[Action]:
        issue_key = issue.get("identifier", "")
        status_name = issue.get("status", "")
        if status_name not in (self.cfg.todo_status, self.cfg.in_progress_status):
            return []

        labels = self._labels(issue.get("labels", []))
        description = issue.get("description", "")

        if not labels.intersection(
            {
                "Type: 📄 Plan",
                "Type: ⭐️ Feature",
                "Type: 🐞 Bug",
                "Type: ⚙️ Chore",
                "Type: 🎨 Design",
                "Type: 🏁 Release",
            }
        ):
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
                        "body": "Missing `Issue Type`. Set one of: `Type: 📄 Plan` `Type: ⭐️ Feature` `Type: 🐞 Bug` `Type: ⚙️ Chore` `Type: 🎨 Design` `Type: 🏁 Release`"
                    },
                ),
                Action("linear", "set_status", issue_key, {"status": self.cfg.backlog_status}),
            ]

        if "Type: 📄 Plan" not in labels and not self._has_estimate(issue):
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
                    {"body": "Missing estimate. Add a Fibonacci estimate before moving this issue into active execution."},
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
        acceptance_required = self._requires_acceptance(labels)
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
        next_status = self.cfg.delivered_status if acceptance_required else self.cfg.done_status
        result_text = "QA SKIPPED" if token == "SKIPPED" else "QA PASSED"
        next_text = "Delivered" if acceptance_required else "Done"
        actions = [
            Action("linear", "set_label", issue_key, {"group": self.cfg.qa_gate_group, "value": gate_value}),
            Action("linear", "set_status", issue_key, {"status": next_status}),
        ]
        actions.extend(
            self._github_comment(target_pr_url, f"{result_text}. Linear moved to {next_text}. {issue_ref}")
        )
        return actions

    def on_linear_acceptance_gate_change(self, issue_key: str, gate_value: str, pr_url: str = "") -> List[Action]:
        if gate_value == self.cfg.pm_rejected:
            actions = [
                Action("linear", "set_status", issue_key, {"status": self.cfg.in_progress_status}),
            ]
            actions.extend(self._github_comment(pr_url, f"ACCEPTANCE REJECTED. See Linear for notes: {issue_key}"))
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
                Action("linear", "set_status", issue_key, {"status": self.cfg.done_status}),
            ]
            actions.extend(
                self._github_comment(pr_url, "ACCEPTANCE SKIPPED BY APPROVED OVERRIDE. Linear status moved to Done.")
            )
            return actions

        return []

    def on_linear_pm_label_change(self, issue_key: str, pm_value: str, pr_url: str = "") -> List[Action]:
        return self.on_linear_acceptance_gate_change(issue_key, pm_value, pr_url)

    def on_github_pr_merged(self, issue: Dict[str, Any], pr_url: str, merge_sha: str) -> List[Action]:
        issue_key = issue.get("identifier", "")
        labels = self._labels(issue.get("labels", []))
        acceptance_required = self._requires_acceptance(labels)
        qa_ok = bool({self.cfg.qa_passed, self.cfg.qa_skipped}.intersection(labels))
        acceptance_ok = (not acceptance_required) or bool(
            {self.cfg.pm_accepted, self.cfg.pm_skipped}.intersection(labels)
        )

        if qa_ok and acceptance_ok:
            return [
                Action(
                    "linear",
                    "comment",
                    issue_key,
                    {"body": f"Merged recorded: {pr_url} | SHA: {merge_sha}. Status should already reflect the gate outcome."},
                )
            ]

        return [
            Action(
                "linear",
                "comment",
                issue_key,
                {
                    "body": "Merged detected but workflow gates are incomplete (need qa-passed/qa-skipped and, for acceptance-required work, pm-accepted/pm-skipped). Manual review required."
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
                out.append(Action("linear", "comment", key, {"body": "Auto-moved to Icebox after 30d inactivity."}))
            elif status == self.cfg.icebox_status and idle_days >= 60:
                out.append(Action("linear", "set_status", key, {"status": self.cfg.obsolete_status}))
                out.append(
                    Action(
                        "linear",
                        "comment",
                        key,
                        {"body": "Auto-closed as Obsolete after 60d inactivity in Icebox."},
                    )
                )

        return out


def format_actions(actions: List[Action]) -> str:
    return json.dumps([a.__dict__ for a in actions], indent=2)
