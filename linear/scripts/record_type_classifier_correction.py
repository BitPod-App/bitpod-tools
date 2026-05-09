#!/usr/bin/env python3
"""
Record a CJ correction to the Linear issue-type classifier in a durable way.

BIT-441 intent:
- keep the human-readable correction log in one place
- ensure every correction also becomes machine-enforced via a test fixture

This script is intentionally simple and local-only (repo mutation).
"""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parents[1]
CORRECTIONS_MD = ROOT / "docs" / "process" / "linear_type_classifier_corrections_v1.md"
FIXTURE_JSON = ROOT / "tests" / "fixtures" / "linear_type_classifier_corrections_v1.json"


def today_iso() -> str:
    return date.today().isoformat()


def append_md_entry(
    *,
    when: str,
    title: str,
    source: str,
    automation_chose: str,
    cj_correction: str,
    rule_learned: str,
    machine_update: str,
) -> None:
    entry = (
        f"\n### {when} — {title}\n\n"
        f"- Source: {source}\n"
        f"- Automation chose: {automation_chose}\n"
        f"- CJ correction: {cj_correction}\n"
        f"- Rule learned: {rule_learned}\n"
        f"- Machine update: {machine_update}\n"
    )

    text = CORRECTIONS_MD.read_text(encoding="utf-8")
    marker = "_No corrections recorded yet._"
    if marker in text:
        text = text.replace(marker, "").rstrip() + "\n"
    CORRECTIONS_MD.write_text(text.rstrip() + "\n" + entry.lstrip(), encoding="utf-8")


def load_fixture() -> List[Dict[str, Any]]:
    if not FIXTURE_JSON.exists():
        return []
    payload = json.loads(FIXTURE_JSON.read_text(encoding="utf-8") or "[]")
    if not isinstance(payload, list):
        raise SystemExit(f"invalid fixture JSON (expected list): {FIXTURE_JSON}")
    return payload


def write_fixture(rows: List[Dict[str, Any]]) -> None:
    FIXTURE_JSON.parent.mkdir(parents=True, exist_ok=True)
    FIXTURE_JSON.write_text(json.dumps(rows, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description="Record a Linear type-classifier correction (BIT-441).")
    ap.add_argument("--date", default=today_iso(), help="Entry date (YYYY-MM-DD). Defaults to today.")
    ap.add_argument("--title", required=True, help="Short correction title.")
    ap.add_argument("--source", required=True, help="BIT-000 or hygiene audit run link.")
    ap.add_argument("--automation-chose", required=True, help="What automation chose (type/route).")
    ap.add_argument("--cj-correction", required=True, help="CJ correction (type/route).")
    ap.add_argument("--rule-learned", required=True, help="One-sentence learned rule.")
    ap.add_argument(
        "--machine-update",
        default="pending",
        help="Classifier rule/test path, or 'pending' (not recommended).",
    )

    ap.add_argument(
        "--intake-json",
        default="",
        help="Optional JSON object containing the classifier intake fields to enforce via test fixture.",
    )
    ap.add_argument(
        "--expected-type",
        default="",
        help="Optional expected canonical type label to enforce for --intake-json (e.g., '⚙️ Chore').",
    )

    args = ap.parse_args()

    if not CORRECTIONS_MD.exists():
        raise SystemExit(f"missing corrections log: {CORRECTIONS_MD}")

    append_md_entry(
        when=args.date,
        title=args.title.strip(),
        source=args.source.strip(),
        automation_chose=args.automation_chose.strip(),
        cj_correction=args.cj_correction.strip(),
        rule_learned=args.rule_learned.strip(),
        machine_update=args.machine_update.strip(),
    )

    if args.intake_json.strip():
        intake: Dict[str, Any] = json.loads(args.intake_json)
        if not isinstance(intake, dict):
            raise SystemExit("--intake-json must be a JSON object")
        if not args.expected_type.strip():
            raise SystemExit("--expected-type is required when --intake-json is set")
        rows = load_fixture()
        rows.append(
            {
                "date": args.date,
                "title": args.title.strip(),
                "source": args.source.strip(),
                "intake": intake,
                "expected_type": args.expected_type.strip(),
            }
        )
        write_fixture(rows)

    print(f"updated: {CORRECTIONS_MD}")
    if args.intake_json.strip():
        print(f"updated: {FIXTURE_JSON}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

