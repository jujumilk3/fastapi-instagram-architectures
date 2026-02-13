from __future__ import annotations

from typing import Any


class Mediator:
    def __init__(self) -> None:
        self._handlers: dict[type, Any] = {}

    def register(self, request_type: type, handler: Any) -> None:
        self._handlers[request_type] = handler

    async def send(self, request: Any) -> Any:
        handler = self._handlers.get(type(request))
        if handler is None:
            raise ValueError(f"No handler registered for {type(request).__name__}")
        return await handler(request)


mediator = Mediator()
