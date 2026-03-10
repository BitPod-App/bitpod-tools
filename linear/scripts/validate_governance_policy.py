#!/usr/bin/env python3
import json
import sys
from pathlib import Path


def fail(msg: str) -> int:
    print(f"FAIL: {msg}")
    return 1


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    policy_path = root / "contracts" / "governance_policy_matrix_v1.json"
    audit_path = root / "examples" / "governance_audit_trail_sample_2026-03-10.json"

    if not policy_path.exists():
        return fail(f"missing policy matrix: {policy_path}")
    if not audit_path.exists():
        return fail(f"missing audit sample: {audit_path}")

    policy = json.loads(policy_path.read_text())
    audit = json.loads(audit_path.read_text())

    classes = {entry["class"] for entry in policy.get("classes", [])}
    if classes != {"A", "B", "C", "D"}:
        return fail(f"unexpected policy classes: {sorted(classes)}")

    if not audit:
        return fail("audit sample empty")

    for row in audit:
        if row["policy_class"] not in classes:
            return fail(f"audit row uses unknown class: {row['policy_class']}")
        if row["decision"] not in {"allowed", "blocked"}:
            return fail(f"invalid decision: {row['decision']}")
        if not row["evidence_links"]:
            return fail("audit row missing evidence_links")

    print("governance policy artifacts PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
