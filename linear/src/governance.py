from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional

try:
    from linear.src.engine import Action
except ModuleNotFoundError:
    from engine import Action


@dataclass
class GovernanceDecision:
    allowed: bool
    policy_class: str
    reason: str


class GovernancePolicy:
    def __init__(self, policy_path: str) -> None:
        self.policy_path = policy_path
        with open(policy_path, "r", encoding="utf-8") as fh:
            raw = json.load(fh)
        self.classes: Dict[str, Dict[str, object]] = {
            item["class"]: item for item in raw.get("classes", [])
        }

    @classmethod
    def default(cls) -> "GovernancePolicy":
        root = Path(__file__).resolve().parents[2]
        policy_path = root / "linear" / "contracts" / "governance_policy_matrix_v1.json"
        return cls(str(policy_path))

    def classify(self, action: Action) -> str:
        if action.system == "github" and action.kind in {"comment", "check_run"}:
            return "A"
        if action.system == "hermes" and action.kind == "enqueue_vera_qa":
            return "A"
        if action.system == "linear" and action.kind == "comment":
            return "A"
        if action.system == "linear" and action.kind in {"set_status", "set_label", "set_label_if_empty"}:
            return "B"
        if action.system == "github" and action.kind in {"merge", "close"}:
            return "C"
        return "C"

    def decide(self, action: Action, dry_run: bool) -> GovernanceDecision:
        policy_class = self.classify(action)
        policy = self.classes.get(policy_class, {})
        approver = str(policy.get("required_approver", "CJ"))
        if dry_run:
            return GovernanceDecision(True, policy_class, "dry-run")
        if approver == "none":
            return GovernanceDecision(True, policy_class, "policy allows live execution")
        if policy_class == "B" and self._guarded_action_is_allowlisted(action):
            return GovernanceDecision(True, policy_class, "guarded action allowlist approved live execution")
        return GovernanceDecision(False, policy_class, f"requires {approver} approval in live mode")

    def allowed_examples(self, policy_class: str) -> List[str]:
        policy = self.classes.get(policy_class, {})
        values = policy.get("allowed_examples", [])
        if isinstance(values, Iterable):
            return [str(v) for v in values]
        return []

    def _guarded_action_is_allowlisted(self, action: Action) -> bool:
        """Return True only for an exact Class-B live rollout action.

        LINEAR_GUARDED_ACTION_ALLOWLIST is intentionally exact-match and narrow:
        comma-separated `system:kind:target` entries such as
        `linear:set_status:BIT-505`. It does not support wildcards.
        """

        if self._vera_qa_result_sync_is_allowed(action):
            return True
        key = f"{action.system}:{action.kind}:{action.target}"
        raw = os.getenv("LINEAR_GUARDED_ACTION_ALLOWLIST", "")
        entries = {entry.strip() for entry in raw.split(",") if entry.strip()}
        return key in entries

    def _vera_qa_result_sync_is_allowed(self, action: Action) -> bool:
        if action.system != "linear":
            return False
        if str(action.payload.get("source_event") or "") != "vera_qa_completed":
            return False
        if action.kind == "set_label":
            group = str(action.payload.get("group") or "")
            value = str(action.payload.get("value") or "")
            if group == "In Review - QA Gate":
                return value in {"qa-passed", "qa-failed", "qa-override"}
            if group == "Blocked By":
                return value == "needs-discussion"
            return False
        if action.kind == "set_status":
            status = str(action.payload.get("status") or "")
            return status in {"Delivered", "In Progress"}
        return False
