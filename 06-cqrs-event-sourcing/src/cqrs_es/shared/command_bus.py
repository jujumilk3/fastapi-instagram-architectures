from collections.abc import Callable
from typing import Any

_handlers: dict[type, Callable] = {}


def register_command_handler(command_type: type, handler: Callable) -> None:
    _handlers[command_type] = handler


async def dispatch_command(command: Any) -> Any:
    handler = _handlers.get(type(command))
    if not handler:
        raise ValueError(f"No handler registered for {type(command).__name__}")
    return await handler(command)


def clear_handlers() -> None:
    _handlers.clear()
