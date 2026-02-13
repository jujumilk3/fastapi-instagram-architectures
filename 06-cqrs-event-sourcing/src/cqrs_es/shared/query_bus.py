from collections.abc import Callable
from typing import Any

_handlers: dict[type, Callable] = {}


def register_query_handler(query_type: type, handler: Callable) -> None:
    _handlers[query_type] = handler


async def dispatch_query(query: Any) -> Any:
    handler = _handlers.get(type(query))
    if not handler:
        raise ValueError(f"No handler registered for {type(query).__name__}")
    return await handler(query)


def clear_handlers() -> None:
    _handlers.clear()
