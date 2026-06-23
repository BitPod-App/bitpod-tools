#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from linear.src.actor_canary import build_default_actor_canary_specs, run_actor_canary_suite
from linear.src.custom_agent_receiver import PeerConfig, ReceiverConfig


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the inert BIT-600 actor attribution/no-cloud-job canary.")
    parser.add_argument("--issue-key", default="BIT-600")
    parser.add_argument("--enable-inert-local-dispatch", action="store_true", help="Evaluate positive receiver route checks without live mutation.")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    receiver_config = ReceiverConfig(
        peers={
            "codex": PeerConfig("codex", enabled=True),
            "claude": PeerConfig("claude", enabled=True),
        },
        local_dispatch_enabled=args.enable_inert_local_dispatch,
    )
    report = run_actor_canary_suite(
        specs=build_default_actor_canary_specs(),
        issue_key=args.issue_key,
        receiver_config=receiver_config,
    )
    if args.format == "json":
        sys.stdout.write(report.to_json())
    else:
        sys.stdout.write(report.to_markdown())
    return 0 if report.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
