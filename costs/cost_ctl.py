#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

WARN_EXIT = 10
FAIL_EXIT = 20


def _load_events(path: Path) -> list[dict]:
    if not path.exists():
        return []
    events = []
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return events


def _event_ts(event: dict) -> datetime | None:
    raw = event.get("recorded_at_utc") or event.get("at_utc")
    if not isinstance(raw, str) or not raw:
        return None
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00")).astimezone(timezone.utc)
    except ValueError:
        return None


def _event_tokens(event: dict) -> int:
    return int(event.get("input_tokens_est", 0) or 0) + int(event.get("output_tokens_est", 0) or 0)


def _status(value: int, warn_cap: int | None, fail_cap: int | None) -> str:
    if fail_cap is not None and value >= fail_cap:
        return "fail"
    if warn_cap is not None and value >= warn_cap:
        return "warn"
    return "ok"


def main() -> int:
    parser = argparse.ArgumentParser(prog="cost_ctl")
    parser.add_argument("--meter", default="/Users/cjarguello/bitpod-app/tools/artifacts/cost-meter/cost_events.jsonl")
    parser.add_argument("--source", default=None)
    parser.add_argument("--window-hours", type=int, default=24)

    parser.add_argument("--run-warn", type=int, default=None, help="Warn when latest run tokens >= this cap")
    parser.add_argument("--run-fail", type=int, default=None, help="Fail when latest run tokens >= this cap")
    parser.add_argument("--daily-warn", type=int, default=None, help="Warn when rolling window tokens >= this cap")
    parser.add_argument("--daily-fail", type=int, default=None, help="Fail when rolling window tokens >= this cap")

    parser.add_argument("--warn-exit-0", action="store_true", help="Return 0 on warn status (still returns non-zero on fail)")
    args = parser.parse_args()

    meter = Path(args.meter).expanduser().resolve()
    events = _load_events(meter)
    if args.source:
        events = [e for e in events if str(e.get("source")) == args.source]

    in_tokens = sum(int(e.get("input_tokens_est", 0) or 0) for e in events)
    out_tokens = sum(int(e.get("output_tokens_est", 0) or 0) for e in events)

    latest_tokens = _event_tokens(events[-1]) if events else 0

    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(hours=max(1, args.window_hours))
    window_events = [e for e in events if (_event_ts(e) and _event_ts(e) >= cutoff)]
    window_tokens = sum(_event_tokens(e) for e in window_events)

    run_status = _status(latest_tokens, args.run_warn, args.run_fail)
    daily_status = _status(window_tokens, args.daily_warn, args.daily_fail)

    overall = "ok"
    if "fail" in {run_status, daily_status}:
        overall = "fail"
    elif "warn" in {run_status, daily_status}:
        overall = "warn"

    payload = {
        "meter": str(meter),
        "events": len(events),
        "input_tokens_est_total": in_tokens,
        "output_tokens_est_total": out_tokens,
        "sources": sorted({str(e.get("source", "unknown")) for e in events}),
        "latest_run_tokens_est": latest_tokens,
        "window_hours": args.window_hours,
        "window_events": len(window_events),
        "window_tokens_est": window_tokens,
        "caps": {
            "run_warn": args.run_warn,
            "run_fail": args.run_fail,
            "daily_warn": args.daily_warn,
            "daily_fail": args.daily_fail,
        },
        "status": {
            "run": run_status,
            "window": daily_status,
            "overall": overall,
        },
    }

    print(json.dumps(payload, indent=2, sort_keys=True))

    if overall == "fail":
        return FAIL_EXIT
    if overall == "warn" and not args.warn_exit_0:
        return WARN_EXIT
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
