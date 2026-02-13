from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable
from typing import Any


class EventBus:
    def __init__(self) -> None:
        self._subscribers: dict[str, list[Callable]] = defaultdict(list)

    def subscribe(self, event_type: str, handler: Callable) -> None:
        self._subscribers[event_type].append(handler)

    async def publish(self, event_type: str, event_data: dict[str, Any]) -> None:
        for handler in self._subscribers.get(event_type, []):
            await handler(event_data)

    def clear(self) -> None:
        self._subscribers.clear()


event_bus = EventBus()
