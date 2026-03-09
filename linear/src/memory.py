from __future__ import annotations

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


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
