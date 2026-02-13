from collections.abc import Callable
from typing import Any

_subscribers: dict[str, list[Callable]] = {}


def subscribe(event_type: str, handler: Callable) -> None:
    if event_type not in _subscribers:
        _subscribers[event_type] = []
    _subscribers[event_type].append(handler)


async def publish(event_type: str, event_data: dict, **kwargs: Any) -> None:
    handlers = _subscribers.get(event_type, [])
    for handler in handlers:
        await handler(event_data, **kwargs)


def clear_subscribers() -> None:
    _subscribers.clear()
