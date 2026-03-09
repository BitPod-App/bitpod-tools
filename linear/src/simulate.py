#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

try:
    from linear.src.engine import LinearBotEngine, format_actions
except ModuleNotFoundError:
    from engine import LinearBotEngine, format_actions


def main() -> int:
    ap = argparse.ArgumentParser(description="Simulate Linear bot event handling")
    ap.add_argument("--event", required=True, help="Path to sample event json")
    ap.add_argument("--mode", required=True, choices=["gh_opened", "gh_review", "linear_comment", "aging_scan"])
    args = ap.parse_args()

    data = json.loads(Path(args.event).read_text())
    bot = LinearBotEngine()

    if args.mode == "gh_opened":
        actions = bot.on_github_pr_opened(data)
    elif args.mode == "gh_review":
        actions = bot.on_github_pr_ready_for_review(data)
    elif args.mode == "linear_comment":
        actions = bot.on_linear_comment(data["issue_key"], data["comment_body"], data.get("pr_url", ""))
    else:
        actions = bot.daily_aging_scan(data["issues"])

    print(format_actions(actions))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
