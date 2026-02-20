#!/usr/bin/env python3
"""CLI wrapper for GPT Bridge HTTP endpoint."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

DEFAULT_URL = "http://127.0.0.1:8787/ask"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Call GPT Bridge /ask endpoint")
    parser.add_argument("message", help="Prompt message")
    parser.add_argument(
        "--task-type",
        default="general",
        choices=["general", "qa_check", "report", "score_check"],
        help="Task type for request schema",
    )
    parser.add_argument(
        "--context-file",
        action="append",
        default=[],
        help="Path to file containing context text; can be used multiple times",
    )
    parser.add_argument(
        "--context-stdin",
        action="store_true",
        help="Append context from stdin",
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=1200,
        help="max_output_tokens hint",
    )
    parser.add_argument(
        "--json-only",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Set constraints.json_only",
    )
    parser.add_argument(
        "--model",
        default=None,
        help="Optional model override (sent as constraints.model)",
    )
    parser.add_argument(
        "--meta",
        default="{}",
        help="JSON object string for meta fields",
    )
    return parser.parse_args()


def load_context(paths: list[str], use_stdin: bool) -> list[str]:
    context: list[str] = []

    for raw_path in paths:
        path = Path(raw_path)
        if not path.exists():
            raise FileNotFoundError(f"Context file not found: {raw_path}")
        context.append(path.read_text(encoding="utf-8"))

    if use_stdin:
        if sys.stdin.isatty():
            raise ValueError("--context-stdin was set but no stdin pipe was provided")
        stdin_text = sys.stdin.read()
        if stdin_text.strip():
            context.append(stdin_text)

    return context


def build_headers() -> dict[str, str]:
    headers = {"Content-Type": "application/json"}

    token = os.getenv("GPT_BRIDGE_TOKEN", "").strip()
    shared_secret = os.getenv("GPT_BRIDGE_SHARED_SECRET", "").strip()

    if token:
        headers["Authorization"] = f"Bearer {token}"
    elif shared_secret:
        headers["X-Bridge-Secret"] = shared_secret

    return headers


def main() -> int:
    args = parse_args()

    try:
        meta = json.loads(args.meta)
    except json.JSONDecodeError as exc:
        print(json.dumps({"error": f"Invalid --meta JSON: {exc}"}), file=sys.stderr)
        return 2
    if not isinstance(meta, dict):
        print(json.dumps({"error": "--meta must decode to a JSON object"}), file=sys.stderr)
        return 2

    try:
        context = load_context(args.context_file, args.context_stdin)
    except (FileNotFoundError, ValueError) as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 2

    constraints: dict[str, Any] = {
        "json_only": bool(args.json_only),
        "max_tokens": args.max_tokens,
    }
    if args.model and args.model.strip():
        constraints["model"] = args.model.strip()

    payload: dict[str, Any] = {
        "task_type": args.task_type,
        "message": args.message,
        "context": context,
        "constraints": constraints,
        "meta": meta,
    }

    url = os.getenv("GPT_BRIDGE_URL", DEFAULT_URL)
    req = Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers=build_headers(),
        method="POST",
    )

    try:
        with urlopen(req, timeout=90) as resp:
            body = resp.read().decode("utf-8")
            print(body)
            return 0
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        print(detail or json.dumps({"error": f"HTTP {exc.code}"}), file=sys.stderr)
        return 1
    except URLError as exc:
        print(json.dumps({"error": f"Connection error: {exc}"}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
