from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class Entity:
    id: int | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime | None = None


@dataclass
class AggregateRoot(Entity):
    _events: list = field(default_factory=list, repr=False, compare=False)

    def add_event(self, event):
        self._events.append(event)

    def collect_events(self) -> list:
        events = self._events.copy()
        self._events.clear()
        return events
