#!/usr/bin/env python3
import argparse
import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Dict, List

from engine import LinearBotEngine, Action, format_actions


def apply_actions(actions: List[Action], dry_run: bool = True) -> None:
    if dry_run:
        print("[DRY_RUN] would apply actions:")
        print(format_actions(actions))
        return
    # Live mutation executor intentionally minimal in v1 bootstrap.
    # Hook real API clients here once credentials and status/label mappings are finalized.
    print("[LIVE] action executor not yet wired; refusing fail-closed.")
    print(format_actions(actions))


class Handler(BaseHTTPRequestHandler):
    bot = LinearBotEngine()
    dry_run = True

    def _json(self, code: int, payload: Dict):
        b = json.dumps(payload).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_POST(self):
        try:
            n = int(self.headers.get("Content-Length", "0"))
            data = json.loads(self.rfile.read(n) or b"{}")
        except Exception as e:
            self._json(400, {"ok": False, "error": f"bad-json: {e}"})
            return

        actions: List[Action] = []
        if self.path == "/github":
            action = data.get("action")
            if action == "opened":
                actions = self.bot.on_github_pr_opened(data)
            elif action == "ready_for_review":
                actions = self.bot.on_github_pr_ready_for_review(data)
            elif action == "closed" and data.get("pull_request", {}).get("merged") is True:
                # merged handling requires hydrated issue labels; use simulation/worker for now
                actions = []
        elif self.path == "/linear":
            kind = data.get("type")
            if kind == "comment_created":
                issue_key = data.get("issue_key", "")
                body = data.get("comment_body", "")
                pr_url = data.get("pr_url", "")
                actions = self.bot.on_linear_comment(issue_key, body, pr_url)
            elif kind == "issue_ready_gate":
                actions = self.bot.on_linear_ready_gate(data.get("issue", {}))
        else:
            self._json(404, {"ok": False, "error": "unknown-path"})
            return

        apply_actions(actions, dry_run=self.dry_run)
        self._json(200, {"ok": True, "actions": [a.__dict__ for a in actions], "dry_run": self.dry_run})


def main() -> int:
    ap = argparse.ArgumentParser(description="Linear bot webhook service")
    ap.add_argument("--host", default=os.getenv("BOT_HOST", "127.0.0.1"))
    ap.add_argument("--port", type=int, default=int(os.getenv("BOT_PORT", "8787")))
    ap.add_argument("--dry-run", action="store_true", default=os.getenv("DRY_RUN", "true").lower() == "true")
    args = ap.parse_args()

    Handler.dry_run = args.dry_run
    httpd = HTTPServer((args.host, args.port), Handler)
    print(f"listening on http://{args.host}:{args.port} dry_run={args.dry_run}")
    httpd.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
