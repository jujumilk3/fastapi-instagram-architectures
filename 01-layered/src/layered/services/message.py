from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from layered.models.message import Message
from layered.repositories.message import MessageRepository
from layered.repositories.user import UserRepository
from layered.schemas.message import ConversationResponse, MessageCreate, MessageResponse


class MessageService:
    def __init__(self, db: AsyncSession):
        self.message_repo = MessageRepository(db)
        self.user_repo = UserRepository(db)

    async def send(self, sender_id: int, data: MessageCreate) -> MessageResponse:
        receiver = await self.user_repo.get_by_id(data.receiver_id)
        if not receiver:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Receiver not found")

        message = Message(sender_id=sender_id, receiver_id=data.receiver_id, content=data.content)
        message = await self.message_repo.create(message)
        return MessageResponse.model_validate(message)

    async def get_conversations(self, user_id: int) -> list[ConversationResponse]:
        convos = await self.message_repo.get_conversations(user_id)
        return [
            ConversationResponse(
                other_user_id=c["other_user_id"],
                last_message=MessageResponse.model_validate(c["last_message"]),
            )
            for c in convos
        ]

    async def get_conversation(
        self, user_id: int, other_user_id: int, limit: int = 50, offset: int = 0
    ) -> list[MessageResponse]:
        messages = await self.message_repo.get_conversation(user_id, other_user_id, limit, offset)
        return [MessageResponse.model_validate(m) for m in messages]

    async def mark_read(self, user_id: int, sender_id: int) -> dict:
        await self.message_repo.mark_as_read(user_id, sender_id)
        return {"status": "ok"}
