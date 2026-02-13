from __future__ import annotations

from abc import ABC, abstractmethod

from ddd.domain.messaging.aggregate import Message


class MessageRepository(ABC):
    @abstractmethod
    async def create(self, message: Message) -> Message: ...

    @abstractmethod
    async def get_conversation(self, user_id: int, other_user_id: int, limit: int, offset: int) -> list[Message]: ...

    @abstractmethod
    async def get_conversations(self, user_id: int) -> list[dict]: ...

    @abstractmethod
    async def mark_as_read(self, user_id: int, sender_id: int) -> None: ...
