from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import case, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from vertical_slice.models.tables import Message


@dataclass
class GetConversationsRequest:
    user_id: int
    db: AsyncSession


@dataclass
class MessageItem:
    id: int
    sender_id: int
    receiver_id: int
    content: str
    is_read: bool
    created_at: datetime


@dataclass
class ConversationItem:
    other_user_id: int
    last_message: MessageItem


async def get_conversations_handler(request: GetConversationsRequest) -> list[ConversationItem]:
    db = request.db
    user_id = request.user_id

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
    result = await db.execute(
        select(Message).join(subq, Message.id == subq.c.last_message_id).order_by(Message.created_at.desc())
    )
    conversations = []
    for m in result.scalars().all():
        other_id = m.receiver_id if m.sender_id == user_id else m.sender_id
        conversations.append(ConversationItem(
            other_user_id=other_id,
            last_message=MessageItem(
                id=m.id, sender_id=m.sender_id, receiver_id=m.receiver_id,
                content=m.content, is_read=m.is_read, created_at=m.created_at,
            ),
        ))
    return conversations
