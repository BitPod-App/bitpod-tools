import json
import re
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Tuple

ISSUE_KEY_RE = re.compile(r"\b([A-Z]{2,}-\d+)\b")
QA_TOKEN_RE = re.compile(r"QA_RESULT=(PASSED|FAILED|OVERRIDE|ACTION_REQUIRED|SKIPPED)")
PR_URL_TOKEN_RE = re.compile(r"PR_URL=(https?://[^\s]+)")
HEAD_SHA_TOKEN_RE = re.compile(r"HEAD_SHA=([0-9a-fA-F]{7,64})")
GITHUB_PR_URL_RE = re.compile(r"https://github\.com/([^/]+)/([^/]+)/pull/(\d+)")
QA_OVERRIDE_COMMAND_RE = re.compile(r"(?im)^/qa-override(?:\s+(.+))?$")
GITHUB_QA_OVERRIDE_LABELS = {"qa_override", "qa-override"}
CJ_OVERRIDE_LOGIN = "cjarguello"

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
CLASSIFIER_CONTRACT_PATH = Path(__file__).resolve().parents[1] / "contracts" / "linear_type_classifier_v1.json"


def _load_classifier_contract() -> Dict[str, Any]:
    with CLASSIFIER_CONTRACT_PATH.open(encoding="utf-8") as f:
        return json.load(f)


CLASSIFIER_CONTRACT = _load_classifier_contract()
CLASSIFICATION_FIELDS = set(CLASSIFIER_CONTRACT["required_intake_fields"])
VALID_OUTPUTS = set(CLASSIFIER_CONTRACT["output_values"])
OUTPUT_ALIASES = {value: value for value in VALID_OUTPUTS}
OUTPUT_ALIASES.update(CLASSIFIER_CONTRACT.get("output_aliases", {}))
STRICT_BOOLEAN_FIELDS = set(CLASSIFIER_CONTRACT["strict_boolean_fields"])
BOOLEAN_VALUES = set(CLASSIFIER_CONTRACT["boolean_values"])



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
    qa_gate_group: str = "In Review - QA Gate"
    acceptance_gate_group: str = "PM Review"

    blocked_needs_specs: str = "needs-specs"
    blocked_needs_type: str = "needs-type"
    blocked_needs_estimate: str = "needs-estimate"

    qa_passed: str = "qa-passed"
    qa_failed: str = "qa-failed"
    qa_override: str = "qa-override"
    blocker_action_required: str = "needs-discussion"

    pm_accepted: str = "pm-accepted"
    pm_rejected: str = "pm-rejected"
    pm_skipped: str = "pm-skipped"

    vera_qa_gate_name: str = "vera-qa-gate"
    vera_assignee: str = "vera"


class LinearBotEngine:
    def __init__(self, config: Optional[BotConfig] = None) -> None:
        self.cfg = config or BotConfig()

    def find_issue_key(self, text: str) -> Optional[str]:
        if not text:
            return None
        m = ISSUE_KEY_RE.search(text)
        return m.group(1) if m else None

    def _issue_keys(self, text: str) -> List[str]:
        if not text:
            return []
        return list(dict.fromkeys(ISSUE_KEY_RE.findall(text)))

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

    def _extract_head_sha_token(self, comment_body: str) -> str:
        m = HEAD_SHA_TOKEN_RE.search(comment_body or "")
        return m.group(1) if m else ""

    def _parse_github_pr_url(self, pr_url: str) -> Tuple[str, str]:
        m = GITHUB_PR_URL_RE.match(pr_url or "")
        if not m:
            return "", ""
        return f"{m.group(1)}/{m.group(2)}", m.group(3)

    def _label_name(self, label: Any) -> str:
        if isinstance(label, dict):
            return str(label.get("name") or "")
        return str(label or "")

    def _has_github_qa_override_label(self, labels: Any) -> bool:
        if not isinstance(labels, list):
            return False
        return any(self._label_name(label).casefold() in GITHUB_QA_OVERRIDE_LABELS for label in labels)

    def _event_sender_login(self, event: Dict[str, Any]) -> str:
        sender = event.get("sender") or {}
        return str(sender.get("login") or sender.get("name") or "")

    def _github_override_pr(self, event: Dict[str, Any]) -> Dict[str, Any]:
        pr = event.get("pull_request") if isinstance(event.get("pull_request"), dict) else {}
        issue = event.get("issue") if isinstance(event.get("issue"), dict) else {}
        if pr:
            return pr
        if issue.get("pull_request") is not None:
            return {
                "number": issue.get("number"),
                "title": issue.get("title"),
                "body": issue.get("body"),
                "html_url": issue.get("html_url"),
                "labels": issue.get("labels", []),
            }
        return {}

    def _github_override_pr_url(self, event: Dict[str, Any]) -> str:
        pr = self._github_override_pr(event)
        return str(pr.get("html_url") or event.get("pr_url") or "")

    def _github_override_labels(self, event: Dict[str, Any]) -> List[Any]:
        labels: List[Any] = []
        pr = self._github_override_pr(event)
        issue = event.get("issue") if isinstance(event.get("issue"), dict) else {}
        for source in (pr.get("labels"), issue.get("labels")):
            if isinstance(source, list):
                labels.extend(source)
        return labels

    def _github_override_head_sha(self, event: Dict[str, Any]) -> str:
        pr = self._github_override_pr(event)
        head = pr.get("head") if isinstance(pr.get("head"), dict) else {}
        return str(head.get("sha") or pr.get("head_sha") or event.get("head_sha") or "")

    def _parse_iso_datetime(self, value: str) -> Optional[datetime]:
        if not value:
            return None
        normalized = value.replace("Z", "+00:00")
        try:
            parsed = datetime.fromisoformat(normalized)
        except ValueError:
            return None
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=timezone.utc)
        return parsed

    def _extract_override_reason_from_body(self, body: str) -> Tuple[str, str]:
        text = body or ""
        command = QA_OVERRIDE_COMMAND_RE.search(text)
        if command:
            reason = (command.group(1) or "").strip()
            if reason:
                return reason, "slash-command"
            lines = text[command.end():].splitlines()
            for line in lines:
                stripped = line.strip()
                if stripped and not stripped.upper().startswith("HEAD_SHA="):
                    return stripped, "slash-command"
            return "", "slash-command"

        return "", ""

    def _github_override_reason(self, event: Dict[str, Any]) -> Dict[str, str]:
        source: Dict[str, Any] = {}
        source_name = ""
        if isinstance(event.get("comment"), dict):
            source = event["comment"]
            source_name = "comment"
        elif isinstance(event.get("review"), dict):
            review = event["review"]
            if str(review.get("state") or "").casefold() != "approved":
                return {}
            source = review
            source_name = "review"
        elif isinstance(event.get("override_reason"), dict):
            source = event["override_reason"]
            source_name = str(source.get("source") or "discovered")

        if not source:
            return {}

        user = source.get("user") if isinstance(source.get("user"), dict) else {}
        actor = str(source.get("actor") or user.get("login") or self._event_sender_login(event))
        body = str(source.get("body") or "")
        reason, format_name = self._extract_override_reason_from_body(body)
        return {
            "actor": actor,
            "body": body,
            "reason": reason,
            "format": format_name,
            "source": source_name,
            "url": str(source.get("html_url") or ""),
            "created_at": str(source.get("created_at") or source.get("submitted_at") or ""),
        }

    def _github_override_issue_key(self, pr: Dict[str, Any], issue: Dict[str, Any]) -> Tuple[str, str]:
        title_keys: List[str] = []
        for title in (str(pr.get("title") or ""), str(issue.get("title") or "")):
            for key in self._issue_keys(title):
                if key not in title_keys:
                    title_keys.append(key)
        if len(title_keys) == 1:
            return title_keys[0], ""
        if len(title_keys) > 1:
            return "", "ambiguous Linear issue keys in PR title"

        body_keys: List[str] = []
        for body in (str(pr.get("body") or ""), str(issue.get("body") or "")):
            for key in self._issue_keys(body):
                if key not in body_keys:
                    body_keys.append(key)
        if len(body_keys) == 1:
            return body_keys[0], ""
        if len(body_keys) > 1:
            return "", "ambiguous Linear issue keys; put the primary issue key in the PR title"
        return "", "missing Linear issue key"

    def _github_override_failure_actions(
        self,
        *,
        pr_url: str,
        repo_full_name: str,
        head_sha: str,
        summary: str,
    ) -> List[Action]:
        actions: List[Action] = []
        if repo_full_name and head_sha:
            actions.extend(
                self._github_check_run(
                    pr_url,
                    repo_full_name,
                    head_sha,
                    "completed",
                    "failure",
                    title="Vera QA override action required",
                    summary=summary,
                )
            )
        return actions

    def on_github_qa_override(self, event: Dict[str, Any]) -> List[Action]:
        pr = self._github_override_pr(event)
        issue = event.get("issue") if isinstance(event.get("issue"), dict) else {}
        pr_url = self._github_override_pr_url(event)
        repo_full_name, _pr_number = self._parse_github_pr_url(pr_url)
        head_sha = self._github_override_head_sha(event)
        issue_key, issue_key_error = self._github_override_issue_key(pr, issue)
        sender = self._event_sender_login(event)
        label_actor = str(event.get("override_label_actor") or "")
        labels = self._github_override_labels(event)
        reason = self._github_override_reason(event)
        missing: List[str] = []

        if sender != CJ_OVERRIDE_LOGIN:
            missing.append(f"override actor must be {CJ_OVERRIDE_LOGIN}")
        if not self._has_github_qa_override_label(labels):
            missing.append("missing GitHub QA_OVERRIDE label")
        if label_actor != CJ_OVERRIDE_LOGIN:
            missing.append("QA_OVERRIDE label must be attributable to cjarguello")
        if reason.get("actor") != CJ_OVERRIDE_LOGIN:
            missing.append("override reason must be authored by cjarguello")
        if not reason.get("reason"):
            missing.append("missing /qa-override <reason>")
        explicit_head = self._extract_head_sha_token(reason.get("body", ""))
        if explicit_head and head_sha:
            explicit = explicit_head.casefold()
            actual = head_sha.casefold()
            if not (actual.startswith(explicit) or explicit.startswith(actual)):
                missing.append("HEAD_SHA does not match current PR head")
        reason_time = self._parse_iso_datetime(reason.get("created_at", ""))
        head_time = self._parse_iso_datetime(str(event.get("head_current_at") or ""))
        if reason_time and head_time and reason_time < head_time:
            missing.append("override reason is stale for current PR head")
        if issue_key_error:
            missing.append(issue_key_error)

        if missing:
            return self._github_override_failure_actions(
                pr_url=pr_url,
                repo_full_name=repo_full_name,
                head_sha=head_sha,
                summary="CJ QA override not accepted: " + "; ".join(missing),
            )

        body = "\n".join(
            [
                "CJ QA override authorized — not Vera QA.",
                f"QA_RESULT=OVERRIDE",
                f"PR_URL={pr_url}",
                f"HEAD_SHA={head_sha}",
                f"Actor: @{CJ_OVERRIDE_LOGIN}",
                f"Reason: {reason['reason']}",
                f"GitHub evidence: {reason.get('url') or 'unavailable'}",
                "",
                "Proof flags after sync request:",
                "VERA_QA_RAN=false",
                "GITHUB_NATIVE_GATE_SATISFIED=true",
                "LINEAR_QA_RESULT_SYNCED=true",
            ]
        )

        actions: List[Action] = [
            Action("linear", "set_label", issue_key, {"group": self.cfg.qa_gate_group, "value": self.cfg.qa_override, "source_event": "github_cj_qa_override"}),
            Action("linear", "set_status", issue_key, {"status": self.cfg.delivered_status, "source_event": "github_cj_qa_override"}),
            Action("linear", "comment", issue_key, {"body": body}),
        ]
        actions.extend(
            self._github_check_run(
                pr_url,
                repo_full_name,
                head_sha,
                "completed",
                "success",
                title="CJ QA override authorized — not Vera QA",
                summary=(
                    f"CJ QA override authorized for {issue_key}; this is not Vera QA. "
                    f"Reason: {reason['reason']}. Evidence: {reason.get('url') or 'unavailable'}"
                ),
            )
        )
        return actions

    def _extract_issue_pr_url(self, issue: Dict[str, Any]) -> str:
        direct = str(issue.get("pr_url") or issue.get("prUrl") or issue.get("pullRequestUrl") or "")
        if direct:
            return direct
        for attachment in issue.get("attachments", []) or []:
            if isinstance(attachment, dict):
                url = str(attachment.get("url") or "")
                if GITHUB_PR_URL_RE.match(url):
                    return url
        return ""

    def _extract_issue_head_sha(self, issue: Dict[str, Any]) -> str:
        github = issue.get("github", {})
        if isinstance(github, dict):
            sha = str(github.get("head_sha") or github.get("headSha") or "")
            if sha:
                return sha
        return str(issue.get("head_sha") or issue.get("headSha") or "")

    def _labels(self, issue_labels: Optional[List[str]]) -> Set[str]:
        return set(issue_labels or [])

    def _truthy(self, value: Any) -> bool:
        return str(value or "").strip().lower() == "yes"

    def _parse_linear_classification(self, description: str) -> Dict[str, str]:
        if not description:
            return {}
        lines = description.splitlines()
        in_block = False
        out: Dict[str, str] = {}
        for raw in lines:
            line = raw.strip()
            if not in_block:
                if line.rstrip(":").lower() == "linear classification":
                    in_block = True
                continue
            if not line:
                if out:
                    break
                continue
            if line.startswith("##") or (not line.startswith("-") and out):
                break
            if not line.startswith("-") or ":" not in line:
                continue
            key, value = line[1:].split(":", 1)
            key = key.strip()
            value = value.strip()
            if key in CLASSIFICATION_FIELDS:
                out[key] = value
        return out

    def _classification_missing_fields(self, intake: Dict[str, str]) -> Set[str]:
        return {field for field in CLASSIFICATION_FIELDS if not intake.get(field)}

    def _normalize_output(self, value: Any) -> str:
        raw = str(value or "").strip().lower()
        return OUTPUT_ALIASES.get(raw, raw)

    def _classification_invalid_fields(self, intake: Dict[str, str]) -> Dict[str, str]:
        invalid: Dict[str, str] = {}
        output = self._normalize_output(intake.get("Output"))
        if output not in VALID_OUTPUTS:
            invalid["Output"] = str(intake.get("Output", ""))
        for field in STRICT_BOOLEAN_FIELDS:
            value = str(intake.get(field, "")).strip().lower()
            if value not in BOOLEAN_VALUES:
                invalid[field] = str(intake.get(field, ""))
        return invalid

    def classify_issue_type(self, intake: Dict[str, str]) -> Tuple[Optional[str], str]:
        invalid = self._classification_invalid_fields(intake)
        if invalid:
            return None, "invalid classifier intake: " + ", ".join(f"{k}={v!r}" for k, v in sorted(invalid.items()))

        output = self._normalize_output(intake.get("Output", ""))
        evidence = str(intake.get("Evidence", "")).strip()
        behavior_change = self._truthy(intake.get("Behavior change"))
        broken = self._truthy(intake.get("Broken existing behavior"))
        children_expected = self._truthy(intake.get("Children expected"))

        for rule in CLASSIFIER_CONTRACT["type_decision_order"]:
            issue_type = rule["type"]
            when = rule["when"]
            if when.get("default"):
                return issue_type, rule["reason"]
            if when.get("evidence_required") and not evidence:
                continue
            if "broken_existing_behavior" in when and when["broken_existing_behavior"] != broken:
                continue
            if "children_expected" in when and when["children_expected"] != children_expected:
                continue
            if "behavior_change" in when and when["behavior_change"] != behavior_change:
                continue
            if "output_any_of" in when and output not in set(when["output_any_of"]):
                continue
            return issue_type, rule["reason"]
        return None, "no classifier rule matched"

    def classify_route(self, issue_type: str, intake: Dict[str, str]) -> Tuple[str, str, str]:
        invalid = self._classification_invalid_fields(intake)
        if invalid:
            return "blocked", "blocked", "invalid classifier intake"
        pm_testable = self._truthy(intake.get("PM-testable"))
        for rule in CLASSIFIER_CONTRACT["routing_defaults"]:
            if "type" in rule and rule["type"] != issue_type:
                continue
            if "type_any_of" in rule and issue_type not in set(rule["type_any_of"]):
                continue
            condition = rule.get("condition", {})
            if "pm_testable" in condition and condition["pm_testable"] != pm_testable:
                continue
            return rule["qa"], rule["pm"], rule["reason"]
        return "required", "required", "default implementation route"

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

    def _github_check_run(
        self,
        pr_url: str,
        repo_full_name: str,
        head_sha: str,
        status: str,
        conclusion: str = "",
        title: str = "",
        summary: str = "",
    ) -> List[Action]:
        if not pr_url or not repo_full_name or not head_sha:
            return []
        payload: Dict[str, Any] = {
            "name": self.cfg.vera_qa_gate_name,
            "repo_full_name": repo_full_name,
            "head_sha": head_sha,
            "status": status,
            "title": title or self.cfg.vera_qa_gate_name,
            "summary": summary or "Vera QA gate update from BitPod auto-QA dispatcher.",
        }
        if conclusion:
            payload["conclusion"] = conclusion
        return [Action("github", "check_run", pr_url, payload)]

    def _vera_dispatch_actions(
        self,
        issue_key: str,
        source_event: str,
        pr_url: str = "",
        repo_full_name: str = "",
        pr_number: str = "",
        head_sha: str = "",
        issue_url: str = "",
    ) -> List[Action]:
        if not issue_key:
            return []
        if pr_url and (not repo_full_name or not pr_number):
            parsed_repo, parsed_number = self._parse_github_pr_url(pr_url)
            repo_full_name = repo_full_name or parsed_repo
            pr_number = pr_number or parsed_number
        stable_repo = repo_full_name or "unknown-repo"
        stable_pr = pr_number or "unknown-pr"
        stable_sha = head_sha or "unknown-sha"
        idempotency_key = f"vera-qa:{issue_key}:{stable_repo}:{stable_pr}:{stable_sha}"
        body_lines = [
            "Vera QA auto-dispatch queued.",
            "",
            f"Issue: {issue_url or issue_key}",
            f"PR: {pr_url or 'unresolved'}",
            f"Head SHA: {head_sha or 'unresolved'}",
            "",
            "Required Vera outputs:",
            "- verification_report.md",
            "- manifest.json",
            "- QA_VERDICT: PASSED|FAILED|OVERRIDE|ACTION_REQUIRED",
            "- QA_RESULT=PASSED|FAILED|OVERRIDE|ACTION_REQUIRED when a terminal GitHub/Linear sync is appropriate",
            "",
            "Proof flags at dispatch:",
            "VERA_QA_RAN=false",
            "GITHUB_NATIVE_GATE_SATISFIED=false",
            "LINEAR_QA_RESULT_SYNCED=false",
            "USER_SEAT_REQUIRED=unknown",
        ]
        dispatch_payload = {
            "assignee": self.cfg.vera_assignee,
            "source_event": source_event,
            "issue_key": issue_key,
            "issue_url": issue_url,
            "pr_url": pr_url,
            "repo_full_name": repo_full_name,
            "pr_number": pr_number,
            "head_sha": head_sha,
            "gate_name": self.cfg.vera_qa_gate_name,
            "idempotency_key": idempotency_key,
            "title": f"Vera QA review: {issue_key}",
            "body": "\n".join(body_lines),
        }
        actions = [
            Action("hermes", "enqueue_vera_qa", issue_key, dispatch_payload),
        ]
        actions.extend(
            self._github_check_run(
                pr_url,
                repo_full_name,
                head_sha,
                "queued",
                title="Vera QA queued",
                summary=(
                    f"Auto-dispatched Vera QA for {issue_key}. "
                    "This queued check is not a pass verdict; branch protection should remain blocked until Vera completes QA."
                ),
            )
        )
        return actions

    def on_github_pr_opened(self, event: Dict[str, Any]) -> List[Action]:
        pr = event.get("pull_request", {})
        issue_key = self._linked_issue_from_pr(pr)
        if not issue_key:
            return [
                Action("github", "comment", str(pr.get("number", "")), {"body": self._issue_linking_comment()})
            ]

        pr_url = str(pr.get("html_url", ""))
        if pr.get("draft") is False:
            repo_full_name, pr_number = self._parse_github_pr_url(pr_url)
            head = pr.get("head", {}) if isinstance(pr.get("head", {}), dict) else {}
            head_sha = str(head.get("sha") or pr.get("head_sha") or "")
            actions = [
                Action("linear", "set_status", issue_key, {"status": self.cfg.in_review_status}),
            ]
            actions.extend(
                self._vera_dispatch_actions(
                    issue_key=issue_key,
                    source_event="github_pr_opened_review_ready",
                    pr_url=pr_url,
                    repo_full_name=repo_full_name,
                    pr_number=pr_number,
                    head_sha=head_sha,
                )
            )
            return actions

        return [
            Action("linear", "set_status", issue_key, {"status": self.cfg.in_progress_status}),
            Action("linear", "comment", issue_key, {"body": f"PR opened: {pr_url}"}),
        ]

    def on_github_pr_ready_for_review(self, event: Dict[str, Any]) -> List[Action]:
        pr = event.get("pull_request", {})
        issue_key = self._linked_issue_from_pr(pr)
        if not issue_key:
            return [
                Action("github", "comment", str(pr.get("number", "")), {"body": self._issue_linking_comment()})
            ]

        pr_url = str(pr.get("html_url", ""))
        repo_full_name, pr_number = self._parse_github_pr_url(pr_url)
        head = pr.get("head", {}) if isinstance(pr.get("head", {}), dict) else {}
        head_sha = str(head.get("sha") or pr.get("head_sha") or "")
        actions = [
            Action("linear", "set_status", issue_key, {"status": self.cfg.in_review_status}),
        ]
        actions.extend(
            self._vera_dispatch_actions(
                issue_key=issue_key,
                source_event="github_pr_ready_for_review",
                pr_url=pr_url,
                repo_full_name=repo_full_name,
                pr_number=pr_number,
                head_sha=head_sha,
            )
        )
        return actions

    def on_github_pr_synchronize(self, event: Dict[str, Any]) -> List[Action]:
        pr = event.get("pull_request", {})
        if pr.get("draft") is True:
            return []
        issue_key = self._linked_issue_from_pr(pr)
        if not issue_key:
            return [
                Action("github", "comment", str(pr.get("number", "")), {"body": self._issue_linking_comment()})
            ]

        pr_url = str(pr.get("html_url", ""))
        repo_full_name, pr_number = self._parse_github_pr_url(pr_url)
        head = pr.get("head", {}) if isinstance(pr.get("head", {}), dict) else {}
        head_sha = str(head.get("sha") or pr.get("head_sha") or "")
        actions = [
            Action("linear", "set_status", issue_key, {"status": self.cfg.in_review_status}),
        ]
        actions.extend(
            self._vera_dispatch_actions(
                issue_key=issue_key,
                source_event="github_pr_synchronize_review_ready",
                pr_url=pr_url,
                repo_full_name=repo_full_name,
                pr_number=pr_number,
                head_sha=head_sha,
            )
        )
        return actions


    def _is_vera_review_request(self, event: Dict[str, Any]) -> bool:
        team = event.get("requested_team") or {}
        reviewer = event.get("requested_reviewer") or {}
        team_slug = str(team.get("slug") or team.get("name") or "").casefold()
        reviewer_login = str(reviewer.get("login") or reviewer.get("name") or "").casefold()
        return team_slug == "veraqa" or reviewer_login == "vera-qa"

    def on_github_pr_review_requested(self, event: Dict[str, Any]) -> List[Action]:
        if not self._is_vera_review_request(event):
            return []
        pr = event.get("pull_request", {})
        issue_key = self._linked_issue_from_pr(pr)
        if not issue_key:
            return [
                Action("github", "comment", str(pr.get("number", "")), {"body": self._issue_linking_comment()})
            ]

        pr_url = str(pr.get("html_url", ""))
        repo_full_name, pr_number = self._parse_github_pr_url(pr_url)
        head = pr.get("head", {}) if isinstance(pr.get("head", {}), dict) else {}
        head_sha = str(head.get("sha") or pr.get("head_sha") or "")
        actions = [
            Action("linear", "set_status", issue_key, {"status": self.cfg.in_review_status}),
        ]
        actions.extend(
            self._vera_dispatch_actions(
                issue_key=issue_key,
                source_event="github_pr_review_requested",
                pr_url=pr_url,
                repo_full_name=repo_full_name,
                pr_number=pr_number,
                head_sha=head_sha,
            )
        )
        return actions

    def on_linear_issue_in_review(self, issue: Dict[str, Any]) -> List[Action]:
        issue_key = str(issue.get("identifier") or issue.get("issue_key") or "")
        status_name = str(issue.get("status") or "")
        if status_name != self.cfg.in_review_status:
            return []
        pr_url = self._extract_issue_pr_url(issue)
        repo_full_name, pr_number = self._parse_github_pr_url(pr_url)
        return self._vera_dispatch_actions(
            issue_key=issue_key,
            source_event="linear_issue_in_review",
            pr_url=pr_url,
            repo_full_name=repo_full_name,
            pr_number=pr_number,
            head_sha=self._extract_issue_head_sha(issue),
            issue_url=str(issue.get("url") or ""),
        )

    def on_vera_qa_completed(self, event: Dict[str, Any]) -> List[Action]:
        issue_key = str(event.get("issue_key") or event.get("identifier") or "")
        qa_result = str(event.get("qa_result") or event.get("qa_verdict") or "").upper()
        pr_url = str(event.get("pr_url") or "")
        head_sha = str(event.get("head_sha") or "")
        issue_url = str(event.get("issue_url") or issue_key)
        report_path = str(event.get("report_path") or "verification_report.md")
        summary = str(event.get("summary") or "Vera QA completed.")
        repo_full_name, _pr_number = self._parse_github_pr_url(pr_url)

        if not issue_key or qa_result not in {"PASSED", "FAILED", "OVERRIDE", "ACTION_REQUIRED"}:
            return []

        if qa_result == "PASSED":
            label_value = self.cfg.qa_passed
            next_status = self.cfg.delivered_status
            gate_conclusion = "success"
            gate_title = "Vera QA passed"
            gate_satisfied = "true"
            result_text = "QA PASSED"
        elif qa_result == "FAILED":
            label_value = self.cfg.qa_failed
            next_status = self.cfg.in_progress_status
            gate_conclusion = "failure"
            gate_title = "Vera QA failed"
            gate_satisfied = "false"
            result_text = "QA FAILED"
        elif qa_result == "OVERRIDE":
            label_value = self.cfg.qa_override
            next_status = self.cfg.delivered_status
            gate_conclusion = "success"
            gate_title = "Vera QA override authorized"
            gate_satisfied = "true"
            result_text = "QA OVERRIDE"
        else:
            label_value = ""
            next_status = ""
            gate_conclusion = "failure"
            gate_title = "Vera QA action required"
            gate_satisfied = "false"
            result_text = "QA ACTION REQUIRED"

        body = "\n".join(
            [
                "Vera QA completed.",
                f"QA_RESULT={qa_result}",
                f"QA_VERDICT: {qa_result}",
                f"PR_URL={pr_url}",
                f"HEAD_SHA={head_sha}",
                f"Report: {report_path}",
                f"Summary: {summary}",
                "",
                "Proof flags after sync request:",
                "VERA_QA_RAN=true",
                f"GITHUB_NATIVE_GATE_SATISFIED={gate_satisfied}",
                "LINEAR_QA_RESULT_SYNCED=true",
                "USER_SEAT_REQUIRED=unknown",
            ]
        )

        actions = []
        if label_value:
            actions.append(
                Action(
                    "linear",
                    "set_label",
                    issue_key,
                    {"group": self.cfg.qa_gate_group, "value": label_value, "source_event": "vera_qa_completed"},
                )
            )
        if next_status:
            actions.append(
                Action(
                    "linear",
                    "set_status",
                    issue_key,
                    {"status": next_status, "source_event": "vera_qa_completed"},
                )
            )
        if qa_result == "ACTION_REQUIRED":
            actions.append(
                Action(
                    "linear",
                    "set_label",
                    issue_key,
                    {"group": self.cfg.blocked_group, "value": self.cfg.blocker_action_required, "source_event": "vera_qa_completed"},
                )
            )
        actions.append(Action("linear", "comment", issue_key, {"body": body}))
        actions.extend(
            self._github_comment(
                pr_url,
                f"{result_text}. Summary: {summary}. Report: {report_path}. See Linear: {issue_url}",
            )
        )
        actions.extend(
            self._github_check_run(
                pr_url,
                repo_full_name,
                head_sha,
                "completed",
                gate_conclusion,
                title=gate_title,
                summary=(
                    f"Vera cannot complete QA until: {summary}. See Linear: {issue_url}"
                    if qa_result == "ACTION_REQUIRED"
                    else f"{gate_title} for {issue_key}. {summary}. See Linear: {issue_url}"
                ),
            )
        )
        return actions

    def on_linear_ready_gate(self, issue: Dict[str, Any]) -> List[Action]:
        issue_key = issue.get("identifier", "")
        status_name = issue.get("status", "")
        if status_name != self.cfg.todo_status:
            return []

        labels = self._labels(issue.get("labels", []))
        description = issue.get("description", "")

        intake = self._parse_linear_classification(description)
        missing_intake = self._classification_missing_fields(intake)
        invalid_intake = self._classification_invalid_fields(intake) if not missing_intake else {}
        if missing_intake:
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
                        "body": "Missing `Linear Classification` block or fields: " + ", ".join(sorted(missing_intake)) + ". Add Output / Behavior change / Broken existing behavior / Evidence / Children expected / PM-testable before moving to Ready."
                    },
                ),
                Action("linear", "set_status", issue_key, {"status": self.cfg.backlog_status}),
            ]

        if invalid_intake:
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
                        "body": "Invalid `Linear Classification` values: " + ", ".join(f"{k}={v!r}" for k, v in sorted(invalid_intake.items())) + ". Use constrained Output values and yes/no boolean fields before moving to Ready."
                    },
                ),
                Action("linear", "set_status", issue_key, {"status": self.cfg.backlog_status}),
            ]

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
                        "body": "Missing or invalid `Issue Type`. Set exactly one canonical type label: `📄 Plan` `⭐️ Feature` `🐞 Bug` `⚙️ Chore` `🎨 Design` `🏁 Release`. Use the machine classifier intake block, not title-only inference."
                    },
                ),
                Action("linear", "set_status", issue_key, {"status": self.cfg.backlog_status}),
            ]

        predicted_type, predicted_reason = self.classify_issue_type(intake)
        actual_type = next(iter(type_labels))
        if predicted_type and actual_type != predicted_type:
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
                        "body": f"Issue Type does not match `Linear Classification` classifier. Label is `{actual_type}` but classifier predicts `{predicted_type}` because {predicted_reason}. Correct the intake block or type label before moving to Ready."
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
                    {"body": "Missing or invalid estimate. Set one of: `1` `2` `3` `5` `8` before moving this issue to Ready."},
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

        # At this point the issue has a valid classifier intake + canonical type.
        # Surface routing defaults with minimal safe automation.
        qa_route, pm_route, route_reason = self.classify_route(actual_type, intake)
        qa_route_display = "override" if qa_route == "skip" else qa_route
        out: List[Action] = [
            Action(
                "linear",
                "comment",
                issue_key,
                {
                    "body": (
                        "Routing recommendation (from `linear_type_classifier_v1.json`): "
                        f"QA={qa_route_display}, PM={pm_route}. Reason: {route_reason}"
                    )
                },
            )
        ]
        if qa_route == "skip":
            out.insert(
                0,
                Action(
                    "linear",
                    "set_label",
                    issue_key,
                    {"group": self.cfg.qa_gate_group, "value": self.cfg.qa_override},
                ),
            )
        return out

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

        head_sha = self._extract_head_sha_token(comment_body)
        repo_full_name, _pr_number = self._parse_github_pr_url(target_pr_url)

        if token == "FAILED":
            actions = [
                Action("linear", "set_label", issue_key, {"group": self.cfg.qa_gate_group, "value": self.cfg.qa_failed}),
                Action("linear", "set_status", issue_key, {"status": self.cfg.in_progress_status}),
            ]
            actions.extend(
                self._github_comment(target_pr_url, f"QA FAILED. Summary: {summary}. See Linear: {issue_ref}")
            )
            actions.extend(
                self._github_check_run(
                    target_pr_url,
                    repo_full_name,
                    head_sha,
                    "completed",
                    "failure",
                    title="Vera QA failed",
                    summary=f"Vera QA failed for {issue_key}. See Linear: {issue_ref}",
                )
            )
            return actions

        if token == "PASSED":
            actions = [
                Action("linear", "set_label", issue_key, {"group": self.cfg.qa_gate_group, "value": self.cfg.qa_passed}),
                Action("linear", "set_status", issue_key, {"status": self.cfg.delivered_status}),
            ]
            actions.extend(
                self._github_comment(target_pr_url, f"QA PASSED. Linear moved to Delivered. {issue_ref}")
            )
            actions.extend(
                self._github_check_run(
                    target_pr_url,
                    repo_full_name,
                    head_sha,
                    "completed",
                    "success",
                    title="Vera QA passed",
                    summary=f"Vera QA passed for {issue_key}. See Linear: {issue_ref}",
                )
            )
            return actions

        if token == "OVERRIDE":
            actions = [
                Action("linear", "set_label", issue_key, {"group": self.cfg.qa_gate_group, "value": self.cfg.qa_override}),
                Action("linear", "set_status", issue_key, {"status": self.cfg.delivered_status}),
            ]
            actions.extend(
                self._github_comment(target_pr_url, f"QA OVERRIDE authorized. Linear moved to Delivered. {issue_ref}")
            )
            actions.extend(
                self._github_check_run(
                    target_pr_url,
                    repo_full_name,
                    head_sha,
                    "completed",
                    "success",
                    title="Vera QA override authorized",
                    summary=f"Authorized QA override for {issue_key}. Reason/evidence: {summary}. See Linear: {issue_ref}",
                )
            )
            return actions

        if token == "ACTION_REQUIRED":
            actions = [
                Action("linear", "set_label", issue_key, {"group": self.cfg.blocked_group, "value": self.cfg.blocker_action_required}),
                Action(
                    "linear",
                    "comment",
                    issue_key,
                    {"body": f"QA_RESULT=ACTION_REQUIRED. Vera cannot complete QA until: {summary}"},
                ),
            ]
            actions.extend(
                self._github_comment(target_pr_url, f"QA ACTION REQUIRED. Vera cannot complete QA until: {summary}. See Linear: {issue_ref}")
            )
            actions.extend(
                self._github_check_run(
                    target_pr_url,
                    repo_full_name,
                    head_sha,
                    "completed",
                    "failure",
                    title="Vera QA action required",
                    summary=f"Vera cannot complete QA until: {summary}. See Linear: {issue_ref}",
                )
            )
            return actions

        if token == "SKIPPED":
            return [
                Action(
                    "linear",
                    "comment",
                    issue_key,
                    {
                        "body": "Deprecated QA_RESULT=SKIPPED ignored. Use QA_RESULT=OVERRIDE with explicit actor, reason, and evidence for an authorized QA bypass."
                    },
                )
            ]

        return []

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
        qa_ok = bool({self.cfg.qa_passed, self.cfg.qa_override}.intersection(labels))
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
            reasons.append("missing qa-passed/qa-override")
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
