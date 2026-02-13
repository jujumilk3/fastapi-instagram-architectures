from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from vertical_slice.models.tables import Message


@dataclass
class GetConversationRequest:
    user_id: int
    other_user_id: int
    limit: int
    offset: int
    db: AsyncSession


@dataclass
class MessageItem:
    id: int
    sender_id: int
    receiver_id: int
    content: str
    is_read: bool
    created_at: datetime


async def get_conversation_handler(request: GetConversationRequest) -> list[MessageItem]:
    db = request.db
    result = await db.execute(
        select(Message).where(
            or_(
                and_(Message.sender_id == request.user_id, Message.receiver_id == request.other_user_id),
                and_(Message.sender_id == request.other_user_id, Message.receiver_id == request.user_id),
            )
        ).order_by(Message.created_at.desc()).limit(request.limit).offset(request.offset)
    )
    return [
        MessageItem(
            id=m.id, sender_id=m.sender_id, receiver_id=m.receiver_id,
            content=m.content, is_read=m.is_read, created_at=m.created_at,
        )
        for m in result.scalars().all()
    ]
