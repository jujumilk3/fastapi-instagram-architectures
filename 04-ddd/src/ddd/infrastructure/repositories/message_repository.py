from __future__ import annotations

from sqlalchemy import and_, case, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from ddd.domain.messaging.aggregate import Message
from ddd.domain.messaging.repository import MessageRepository
from ddd.infrastructure.orm.mapper import message_model_to_entity
from ddd.infrastructure.orm.models import MessageModel


class SqlAlchemyMessageRepository(MessageRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, message: Message) -> Message:
        m = MessageModel(
            sender_id=message.sender_id,
            receiver_id=message.receiver_id,
            content=message.content,
        )
        self.db.add(m)
        await self.db.flush()
        await self.db.refresh(m)
        return message_model_to_entity(m)

    async def get_conversation(
        self, user_id: int, other_user_id: int, limit: int, offset: int
    ) -> list[Message]:
        r = await self.db.execute(
            select(MessageModel)
            .where(
                or_(
                    and_(
                        MessageModel.sender_id == user_id,
                        MessageModel.receiver_id == other_user_id,
                    ),
                    and_(
                        MessageModel.sender_id == other_user_id,
                        MessageModel.receiver_id == user_id,
                    ),
                )
            )
            .order_by(MessageModel.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return [message_model_to_entity(m) for m in r.scalars().all()]

    async def get_conversations(self, user_id: int) -> list[dict]:
        other_user = case(
            (MessageModel.sender_id == user_id, MessageModel.receiver_id),
            else_=MessageModel.sender_id,
        )
        subq = (
            select(
                other_user.label("other_user_id"),
                func.max(MessageModel.id).label("last_message_id"),
            )
            .where(
                or_(
                    MessageModel.sender_id == user_id,
                    MessageModel.receiver_id == user_id,
                )
            )
            .group_by(other_user)
            .subquery()
        )
        r = await self.db.execute(
            select(MessageModel)
            .join(subq, MessageModel.id == subq.c.last_message_id)
            .order_by(MessageModel.created_at.desc())
        )
        return [
            {
                "other_user_id": (
                    m.receiver_id if m.sender_id == user_id else m.sender_id
                ),
                "last_message": message_model_to_entity(m),
            }
            for m in r.scalars().all()
        ]

    async def mark_as_read(self, user_id: int, sender_id: int) -> None:
        r = await self.db.execute(
            select(MessageModel).where(
                MessageModel.sender_id == sender_id,
                MessageModel.receiver_id == user_id,
                MessageModel.is_read.is_(False),
            )
        )
        for m in r.scalars().all():
            m.is_read = True
        await self.db.flush()
