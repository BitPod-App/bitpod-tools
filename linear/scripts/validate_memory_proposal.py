#!/usr/bin/env python3
import csv
import json
import sys
from pathlib import Path


def fail(msg: str) -> int:
    print(f"FAIL: {msg}")
    return 1


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    proposal_path = root / "examples" / "memory_write_proposal_example_v1.json"
    schema_path = root / "contracts" / "memory_write_proposal_schema_v1.json"
    approval_log_path = root / "examples" / "memory_approval_log_v1.csv"
    contradiction_scan_path = root / "examples" / "memory_contradiction_scan_sample_2026-03-10.md"

    if not proposal_path.exists():
      return fail(f"missing proposal: {proposal_path}")
    if not schema_path.exists():
      return fail(f"missing schema: {schema_path}")
    if not approval_log_path.exists():
      return fail(f"missing approval log: {approval_log_path}")
    if not contradiction_scan_path.exists():
      return fail(f"missing contradiction scan: {contradiction_scan_path}")

    proposal = json.loads(proposal_path.read_text())
    schema = json.loads(schema_path.read_text())
    required = set(schema.get("required", []))
    missing = sorted(required - set(proposal.keys()))
    if missing:
        return fail(f"proposal missing required fields: {missing}")

    if proposal["approval"]["state"] not in {"proposed", "approved", "rejected"}:
        return fail("invalid approval.state")
    if proposal["contradiction_status"] not in {"clear", "needs_review", "conflict"}:
        return fail("invalid contradiction_status")

    with approval_log_path.open(newline="") as fh:
        rows = list(csv.DictReader(fh))
    if not rows:
        return fail("approval log empty")
    if rows[0]["proposal_id"] != proposal["proposal_id"]:
        return fail("approval log proposal_id mismatch")

    if "Taylor remains the approval gate" not in contradiction_scan_path.read_text():
        return fail("contradiction scan missing core rule")

    print("memory proposal artifacts PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
