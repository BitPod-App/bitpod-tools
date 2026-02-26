#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
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


def _event_usd(event: dict, usd_per_1k_in: float, usd_per_1k_out: float) -> float:
    in_tokens = float(event.get("input_tokens_est", 0) or 0)
    out_tokens = float(event.get("output_tokens_est", 0) or 0)
    return (in_tokens / 1000.0) * usd_per_1k_in + (out_tokens / 1000.0) * usd_per_1k_out


def _status(value: int, warn_cap: int | None, fail_cap: int | None) -> str:
    if fail_cap is not None and value >= fail_cap:
        return "fail"
    if warn_cap is not None and value >= warn_cap:
        return "warn"
    return "ok"


def _flt_env(name: str, default: float) -> float:
    raw = os.getenv(name)
    if raw is None or raw == "":
        return default
    try:
        return float(raw)
    except ValueError:
        return default


def main() -> int:
    parser = argparse.ArgumentParser(prog="cost_ctl")
    parser.add_argument("--meter", default="/Users/cjarguello/bitpod-app/tools/artifacts/cost-meter/cost_events.jsonl")
    parser.add_argument("--source", default=None)
    parser.add_argument("--window-hours", type=int, default=24)

    parser.add_argument("--run-warn", type=int, default=None, help="Warn when latest run tokens >= this cap")
    parser.add_argument("--run-fail", type=int, default=None, help="Fail when latest run tokens >= this cap")
    parser.add_argument("--daily-warn", type=int, default=None, help="Warn when rolling window tokens >= this cap")
    parser.add_argument("--daily-fail", type=int, default=None, help="Fail when rolling window tokens >= this cap")

    parser.add_argument("--usd-per-1k-in", type=float, default=_flt_env("COST_USD_PER_1K_IN", 0.0))
    parser.add_argument("--usd-per-1k-out", type=float, default=_flt_env("COST_USD_PER_1K_OUT", 0.0))
    parser.add_argument("--weekly-budget-usd", type=float, default=_flt_env("COST_WEEKLY_BUDGET_USD", 0.0))
    parser.add_argument("--monthly-budget-usd", type=float, default=_flt_env("COST_MONTHLY_BUDGET_USD", 0.0))

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

    week_cutoff = now - timedelta(days=7)
    month_cutoff = now - timedelta(days=30)
    week_events = [e for e in events if (_event_ts(e) and _event_ts(e) >= week_cutoff)]
    month_events = [e for e in events if (_event_ts(e) and _event_ts(e) >= month_cutoff)]

    total_usd = sum(_event_usd(e, args.usd_per_1k_in, args.usd_per_1k_out) for e in events)
    latest_usd = _event_usd(events[-1], args.usd_per_1k_in, args.usd_per_1k_out) if events else 0.0
    window_usd = sum(_event_usd(e, args.usd_per_1k_in, args.usd_per_1k_out) for e in window_events)
    week_usd = sum(_event_usd(e, args.usd_per_1k_in, args.usd_per_1k_out) for e in week_events)
    month_usd = sum(_event_usd(e, args.usd_per_1k_in, args.usd_per_1k_out) for e in month_events)

    run_status = _status(latest_tokens, args.run_warn, args.run_fail)
    daily_status = _status(window_tokens, args.daily_warn, args.daily_fail)

    overall = "ok"
    if "fail" in {run_status, daily_status}:
        overall = "fail"
    elif "warn" in {run_status, daily_status}:
        overall = "warn"

    weekly_budget_usd = args.weekly_budget_usd if args.weekly_budget_usd > 0 else None
    monthly_budget_usd = args.monthly_budget_usd if args.monthly_budget_usd > 0 else None

    weekly_used_pct = (week_usd / weekly_budget_usd * 100.0) if weekly_budget_usd else None
    monthly_used_pct = (month_usd / monthly_budget_usd * 100.0) if monthly_budget_usd else None
    weekly_budgets_burned_month = (month_usd / weekly_budget_usd) if weekly_budget_usd else None

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
        "pricing": {
            "usd_per_1k_in": args.usd_per_1k_in,
            "usd_per_1k_out": args.usd_per_1k_out,
        },
        "usd_estimates": {
            "latest_run_usd": round(latest_usd, 6),
            "window_usd": round(window_usd, 6),
            "week_usd": round(week_usd, 6),
            "month_usd": round(month_usd, 6),
            "total_usd": round(total_usd, 6),
        },
        "budgets": {
            "weekly_budget_usd": weekly_budget_usd,
            "monthly_budget_usd": monthly_budget_usd,
            "weekly_used_pct": round(weekly_used_pct, 3) if weekly_used_pct is not None else None,
            "monthly_used_pct": round(monthly_used_pct, 3) if monthly_used_pct is not None else None,
            "weekly_budgets_burned_this_month": round(weekly_budgets_burned_month, 6)
            if weekly_budgets_burned_month is not None
            else None,
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
