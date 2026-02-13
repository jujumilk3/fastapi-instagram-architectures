from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from vertical_slice.models.tables import Message, User


@dataclass
class SendMessageRequest:
    sender_id: int
    receiver_id: int
    content: str
    db: AsyncSession


@dataclass
class SendMessageResponse:
    id: int
    sender_id: int
    receiver_id: int
    content: str
    is_read: bool
    created_at: datetime


async def send_message_handler(request: SendMessageRequest) -> SendMessageResponse:
    db = request.db
    receiver = await db.get(User, request.receiver_id)
    if not receiver:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Receiver not found")

    message = Message(sender_id=request.sender_id, receiver_id=request.receiver_id, content=request.content)
    db.add(message)
    await db.flush()
    await db.refresh(message)

    return SendMessageResponse(
        id=message.id,
        sender_id=message.sender_id,
        receiver_id=message.receiver_id,
        content=message.content,
        is_read=message.is_read,
        created_at=message.created_at,
    )
