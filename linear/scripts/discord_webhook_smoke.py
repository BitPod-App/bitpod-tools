#!/usr/bin/env python3
"""Send or simulate one smoke message per Discord webhook target.

Usage:
  python3 linear/scripts/discord_webhook_smoke.py --config linear/config.discord.example.json --dry-run
"""

import argparse
import json
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Discord webhook smoke sender")
    ap.add_argument("--config", required=True, help="Path to JSON config with webhook URLs")
    ap.add_argument("--dry-run", action="store_true", help="Do not send; print masked targets only")
    ap.add_argument("--timeout", type=float, default=8.0, help="HTTP timeout seconds")
    return ap.parse_args()


def mask_url(url: str) -> str:
    if not url:
        return "<missing>"
    if len(url) <= 24:
        return "<short-url>"
    return url[:22] + "..." + url[-6:]


def send(url: str, content: str, timeout: float) -> tuple[bool, str]:
    body = json.dumps({"content": content}).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            status = resp.getcode()
        return (200 <= status < 300, f"HTTP {status}")
    except Exception as exc:  # noqa: BLE001
        return (False, str(exc))


def main() -> int:
    args = parse_args()
    cfg = json.loads(Path(args.config).read_text())
    webhooks = cfg.get("webhooks", {})
    prefix = cfg.get("message_prefix", "[BitPod parity]")

    required = ["ops_status", "build", "review_qa", "release", "incidents"]
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")

    missing = [k for k in required if not webhooks.get(k)]
    if missing:
        print("MISSING_WEBHOOK_KEYS:", ", ".join(missing))
        return 2

    print(f"RUN_MODE={'DRY_RUN' if args.dry_run else 'LIVE'} UTC={now}")
    failures = 0
    for key in required:
        msg = f"{prefix} smoke:{key} utc:{now}"
        url = webhooks[key]
        if args.dry_run:
            print(f"[DRY] {key}: target={mask_url(url)} payload={msg}")
            continue

        ok, detail = send(url, msg, args.timeout)
        state = "PASS" if ok else "FAIL"
        print(f"[{state}] {key}: target={mask_url(url)} result={detail}")
        if not ok:
            failures += 1

    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
