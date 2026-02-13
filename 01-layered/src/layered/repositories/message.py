from sqlalchemy import and_, case, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from layered.models.message import Message


class MessageRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, message: Message) -> Message:
        self.db.add(message)
        await self.db.flush()
        await self.db.refresh(message)
        return message

    async def get_conversation(
        self, user_id: int, other_user_id: int, limit: int = 50, offset: int = 0
    ) -> list[Message]:
        result = await self.db.execute(
            select(Message)
            .where(
                or_(
                    and_(Message.sender_id == user_id, Message.receiver_id == other_user_id),
                    and_(Message.sender_id == other_user_id, Message.receiver_id == user_id),
                )
            )
            .order_by(Message.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def get_conversations(self, user_id: int) -> list[dict]:
        # Get the latest message per conversation partner
        other_user = case(
            (Message.sender_id == user_id, Message.receiver_id),
            else_=Message.sender_id,
        )
        subq = (
            select(
                other_user.label("other_user_id"),
                func.max(Message.id).label("last_message_id"),
            )
            .where(or_(Message.sender_id == user_id, Message.receiver_id == user_id))
            .group_by(other_user)
            .subquery()
        )
        result = await self.db.execute(
            select(Message)
            .join(subq, Message.id == subq.c.last_message_id)
            .order_by(Message.created_at.desc())
        )
        messages = result.scalars().all()
        return [
            {
                "other_user_id": m.receiver_id if m.sender_id == user_id else m.sender_id,
                "last_message": m,
            }
            for m in messages
        ]

    async def mark_as_read(self, user_id: int, sender_id: int) -> None:
        result = await self.db.execute(
            select(Message).where(
                Message.sender_id == sender_id,
                Message.receiver_id == user_id,
                Message.is_read.is_(False),
            )
        )
        for msg in result.scalars().all():
            msg.is_read = True
        await self.db.flush()
