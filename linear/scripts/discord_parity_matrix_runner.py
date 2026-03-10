#!/usr/bin/env python3
"""Run Discord parity matrix checks and emit a Markdown report.

Config format matches linear/config.discord.example.json
with an extra optional `routes` object for matrix row mapping.
"""

import argparse
import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

USER_AGENT = "BitPod-Discord-Diagnostic/1.0"

ROWS = [
    ("GH_PR_OPENED", "build", "repo,pr,title,author,link"),
    ("GH_CHECK_FAILED", "incidents", "repo,check,run,severity"),
    ("GH_PR_MERGED", "release", "repo,pr,sha,link"),
    ("LINEAR_IN_REVIEW", "review_qa", "issue,title,assignee,link"),
    ("LINEAR_PRIORITY_ESCALATED", "ops_status", "issue,old,new,link"),
    ("RUNTIME_QA_SUMMARY", "review_qa", "issue,result,artifacts"),
    ("RUNTIME_INCIDENT", "incidents", "service,symptom,next_action"),
]


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Discord parity matrix runner")
    ap.add_argument("--config", required=True)
    ap.add_argument("--report", required=True, help="Output markdown report path")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--timeout", type=float, default=8.0)
    return ap.parse_args()


def mask(url: str) -> str:
    if len(url) < 24:
        return "<short-url>"
    return f"{url[:22]}...{url[-6:]}"


def post(url: str, content: str, timeout: float) -> tuple[bool, str]:
    data = json.dumps({"content": content}).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("User-Agent", USER_AGENT)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            code = resp.getcode()
        return (200 <= code < 300, f"HTTP {code}")
    except Exception as exc:  # noqa: BLE001
        return (False, str(exc))


def main() -> int:
    args = parse_args()
    cfg = json.loads(Path(args.config).read_text())
    webhooks = cfg.get("webhooks", {})
    prefix = cfg.get("message_prefix", "[BitPod parity]")

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")
    results = []

    for event_name, route_key, expected_fields in ROWS:
        url = webhooks.get(route_key, "")
        if not url:
            results.append((event_name, route_key, expected_fields, False, "MISSING_WEBHOOK"))
            continue

        payload = f"{prefix} event:{event_name} utc:{ts} fields:{expected_fields}"
        if args.dry_run:
            results.append((event_name, route_key, expected_fields, True, f"DRY_RUN target={mask(url)}"))
            continue

        ok, detail = post(url, payload, args.timeout)
        results.append((event_name, route_key, expected_fields, ok, detail))

    report_lines = [
        "# Discord Parity Matrix Report",
        "",
        f"- UTC: {ts}",
        f"- Mode: {'DRY_RUN' if args.dry_run else 'LIVE'}",
        f"- Config: `{args.config}`",
        "",
        "| Event | Route | Expected Fields | Result | Detail |",
        "|---|---|---|---|---|",
    ]

    failures = 0
    for event_name, route_key, expected_fields, ok, detail in results:
        result = "PASS" if ok else "FAIL"
        if not ok:
            failures += 1
        report_lines.append(f"| {event_name} | {route_key} | `{expected_fields}` | {result} | {detail} |")

    report_lines.extend([
        "",
        f"- Summary: {len(results) - failures} passed / {failures} failed",
    ])

    out = Path(args.report)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(report_lines) + "\n")
    print(f"WROTE_REPORT {out}")
    print(f"SUMMARY pass={len(results)-failures} fail={failures}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
