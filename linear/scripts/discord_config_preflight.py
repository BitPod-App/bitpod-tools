#!/usr/bin/env python3
"""Validate the private Discord config before any live webhook call."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REQUIRED_ROUTES = ["ops_status", "build", "review_qa", "release", "incidents"]
WEBHOOK_RE = re.compile(r"^https://discord\.com/api/webhooks/\d+/[\w-]+$")


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Validate Discord config shape")
    ap.add_argument("--config", required=True, help="Path to Discord config JSON")
    return ap.parse_args()


def fail(msg: str) -> int:
    print(f"FAIL: {msg}")
    return 1


def main() -> int:
    args = parse_args()
    cfg_path = Path(args.config)
    if not cfg_path.exists():
        return fail(f"config not found: {cfg_path}")

    cfg = json.loads(cfg_path.read_text())
    discord = cfg.get("discord", {})
    webhooks = cfg.get("webhooks", {})
    channels = discord.get("channels", {})

    server_id = discord.get("server_id", "")
    if not server_id or server_id.startswith("REPLACE_"):
        return fail("discord.server_id is missing or placeholder")

    for route in REQUIRED_ROUTES:
        ch = channels.get(route, {})
        ch_id = ch.get("id", "")
        url = webhooks.get(route, "")
        if not ch_id or ch_id.startswith("REPLACE_"):
            return fail(f"channel id missing for route: {route}")
        if not url or url.startswith("https://discord.com/api/webhooks/REPLACE/REPLACE"):
            return fail(f"webhook missing for route: {route}")
        if not WEBHOOK_RE.match(url):
            return fail(f"webhook format invalid for route: {route}")

    print("discord config preflight PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
