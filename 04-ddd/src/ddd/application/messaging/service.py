from __future__ import annotations

from fastapi import HTTPException, status

from ddd.domain.messaging.aggregate import Message
from ddd.domain.messaging.repository import MessageRepository
from ddd.domain.user.repository import UserRepository


class MessageApplicationService:
    def __init__(self, message_repo: MessageRepository, user_repo: UserRepository):
        self.message_repo = message_repo
        self.user_repo = user_repo

    async def send(
        self, sender_id: int, receiver_id: int, content: str
    ) -> Message:
        if not await self.user_repo.get_by_id(receiver_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Receiver not found"
            )
        return await self.message_repo.create(
            Message(sender_id=sender_id, receiver_id=receiver_id, content=content)
        )

    async def get_conversations(self, user_id: int) -> list[dict]:
        return await self.message_repo.get_conversations(user_id)

    async def get_conversation(
        self, user_id: int, other_user_id: int, limit: int, offset: int
    ) -> list[Message]:
        return await self.message_repo.get_conversation(
            user_id, other_user_id, limit, offset
        )

    async def mark_read(self, user_id: int, sender_id: int) -> dict:
        await self.message_repo.mark_as_read(user_id, sender_id)
        return {"status": "ok"}
