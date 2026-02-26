#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


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


def main() -> int:
    parser = argparse.ArgumentParser(prog="cost_ctl")
    parser.add_argument("--meter", default="/Users/cjarguello/bitpod-app/tools/artifacts/cost-meter/cost_events.jsonl")
    parser.add_argument("--source", default=None)
    args = parser.parse_args()

    meter = Path(args.meter).expanduser().resolve()
    events = _load_events(meter)
    if args.source:
        events = [e for e in events if str(e.get("source")) == args.source]

    in_tokens = sum(int(e.get("input_tokens_est", 0) or 0) for e in events)
    out_tokens = sum(int(e.get("output_tokens_est", 0) or 0) for e in events)

    print(json.dumps({
        "meter": str(meter),
        "events": len(events),
        "input_tokens_est_total": in_tokens,
        "output_tokens_est_total": out_tokens,
        "sources": sorted({str(e.get("source", "unknown")) for e in events}),
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
