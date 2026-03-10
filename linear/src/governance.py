from __future__ import annotations

import json
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
        if action.system == "github" and action.kind == "comment":
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
        return GovernanceDecision(False, policy_class, f"requires {approver} approval in live mode")

    def allowed_examples(self, policy_class: str) -> List[str]:
        policy = self.classes.get(policy_class, {})
        values = policy.get("allowed_examples", [])
        if isinstance(values, Iterable):
            return [str(v) for v in values]
        return []
