from __future__ import annotations

import json
from datetime import datetime, timezone
from math import ceil
from pathlib import Path
from typing import Any


def estimate_tokens_from_text(text: str) -> int:
    """Rough text-token estimate for planning/monitoring, not billing-accurate."""
    if not text:
        return 0
    return ceil(len(text) / 4)


def excerpt_text(text: str, max_chars: int = 6000) -> str:
    if len(text) <= max_chars:
        return text
    head = max_chars // 2
    tail = max_chars - head
    return text[:head] + "\n\n[...TRUNCATED FOR COST CONTROL...]\n\n" + text[-tail:]


def append_cost_event(meter_file: Path, event: dict[str, Any]) -> None:
    meter_file.parent.mkdir(parents=True, exist_ok=True)
    payload = {"recorded_at_utc": datetime.now(timezone.utc).isoformat(), **event}
    with meter_file.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, sort_keys=True) + "\n")
