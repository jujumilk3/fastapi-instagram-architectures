from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from vertical_slice.models.tables import Message


@dataclass
class MarkMessagesReadRequest:
    user_id: int
    sender_id: int
    db: AsyncSession


async def mark_messages_read_handler(request: MarkMessagesReadRequest) -> dict:
    db = request.db
    result = await db.execute(
        select(Message).where(
            Message.sender_id == request.sender_id,
            Message.receiver_id == request.user_id,
            Message.is_read.is_(False),
        )
    )
    for msg in result.scalars().all():
        msg.is_read = True
    await db.flush()
    return {"status": "ok"}
