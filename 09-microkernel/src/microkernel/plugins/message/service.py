from fastapi import HTTPException, status
from sqlalchemy import and_, case, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from microkernel.plugins.auth.models import User
from microkernel.plugins.message.models import Message
from microkernel.plugins.message.schemas import ConversationResponse, MessageCreate, MessageResponse


class MessageService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def send(self, sender_id: int, data: MessageCreate) -> MessageResponse:
        receiver = await self.db.get(User, data.receiver_id)
        if not receiver:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Receiver not found")
        message = Message(sender_id=sender_id, receiver_id=data.receiver_id, content=data.content)
        self.db.add(message)
        await self.db.flush()
        await self.db.refresh(message)
        return MessageResponse.model_validate(message)

    async def get_conversations(self, user_id: int) -> list[ConversationResponse]:
        other_user = case(
            (Message.sender_id == user_id, Message.receiver_id),
            else_=Message.sender_id,
        )
        subq = (
            select(other_user.label("other_user_id"), func.max(Message.id).label("last_message_id"))
            .where(or_(Message.sender_id == user_id, Message.receiver_id == user_id))
            .group_by(other_user)
            .subquery()
        )
        result = await self.db.execute(
            select(Message).join(subq, Message.id == subq.c.last_message_id).order_by(Message.created_at.desc())
        )
        return [
            ConversationResponse(
                other_user_id=m.receiver_id if m.sender_id == user_id else m.sender_id,
                last_message=MessageResponse.model_validate(m),
            )
            for m in result.scalars().all()
        ]

    async def get_conversation(self, user_id: int, other_user_id: int, limit: int = 50, offset: int = 0) -> list[MessageResponse]:
        result = await self.db.execute(
            select(Message).where(
                or_(
                    and_(Message.sender_id == user_id, Message.receiver_id == other_user_id),
                    and_(Message.sender_id == other_user_id, Message.receiver_id == user_id),
                )
            ).order_by(Message.created_at.desc()).limit(limit).offset(offset)
        )
        return [MessageResponse.model_validate(m) for m in result.scalars().all()]

    async def mark_read(self, user_id: int, sender_id: int) -> dict:
        result = await self.db.execute(
            select(Message).where(
                Message.sender_id == sender_id, Message.receiver_id == user_id, Message.is_read.is_(False)
            )
        )
        for msg in result.scalars().all():
            msg.is_read = True
        await self.db.flush()
        return {"status": "ok"}
