import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class Message:
    pass


@dataclass
class Ask(Message):
    """Message that expects a response via an embedded Future."""
    _future: asyncio.Future = field(default_factory=lambda: asyncio.get_running_loop().create_future())

    def reply(self, result):
        if not self._future.done():
            self._future.set_result(result)

    def fail(self, error: Exception):
        if not self._future.done():
            self._future.set_exception(error)

    async def response(self):
        return await self._future


class Actor(ABC):
    def __init__(self):
        self._mailbox: asyncio.Queue = asyncio.Queue()
        self._running = False
        self._task: asyncio.Task | None = None

    async def start(self):
        self._running = True
        self._task = asyncio.create_task(self._run())

    async def _run(self):
        while self._running:
            try:
                message = await asyncio.wait_for(self._mailbox.get(), timeout=0.5)
            except asyncio.TimeoutError:
                continue
            try:
                await self.receive(message)
            except Exception as exc:
                if isinstance(message, Ask) and not message._future.done():
                    message.fail(exc)

    async def send(self, message: Message):
        await self._mailbox.put(message)

    @abstractmethod
    async def receive(self, message: Message) -> None: ...

    async def stop(self):
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
