from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List, Protocol


@dataclass
class MemoryEvent:
    key: str
    kind: str
    payload: Dict[str, str]
    at: str


class MemoryStore(Protocol):
    def append(self, event: MemoryEvent) -> None:
        ...

    def list_for(self, key: str) -> List[MemoryEvent]:
        ...


class InMemoryStore:
    """Default local dev store; replace with durable backend in cloud runtime."""

    def __init__(self) -> None:
        self._items: Dict[str, List[MemoryEvent]] = {}

    def append(self, event: MemoryEvent) -> None:
        self._items.setdefault(event.key, []).append(event)

    def list_for(self, key: str) -> List[MemoryEvent]:
        return list(self._items.get(key, []))


class JsonlFileStore:
    """Append-only local sink for runtime trace durability."""

    def __init__(self, path: str) -> None:
        self.path = path

    def append(self, event: MemoryEvent) -> None:
        parent = os.path.dirname(self.path)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(self.path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(event.__dict__) + "\n")

    def list_for(self, key: str) -> List[MemoryEvent]:
        if not os.path.exists(self.path):
            return []
        out: List[MemoryEvent] = []
        with open(self.path, "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                raw = json.loads(line)
                if raw.get("key") == key:
                    out.append(
                        MemoryEvent(
                            key=raw["key"],
                            kind=raw["kind"],
                            payload=raw.get("payload", {}),
                            at=raw["at"],
                        )
                    )
        return out


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
