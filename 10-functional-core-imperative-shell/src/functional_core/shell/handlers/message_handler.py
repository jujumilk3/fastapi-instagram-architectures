from fastapi import HTTPException, status
from sqlalchemy import and_, case, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from functional_core.shell.models import Message, User


async def send_message(
    db: AsyncSession, sender_id: int, receiver_id: int, content: str
) -> Message:
    receiver = await db.get(User, receiver_id)
    if not receiver:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Receiver not found")

    message = Message(sender_id=sender_id, receiver_id=receiver_id, content=content)
    db.add(message)
    await db.flush()
    await db.refresh(message)
    return message


async def get_conversations(db: AsyncSession, user_id: int) -> list[dict]:
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
    result = await db.execute(
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


async def get_conversation(
    db: AsyncSession, user_id: int, other_user_id: int, limit: int = 50, offset: int = 0
) -> list[Message]:
    result = await db.execute(
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


async def mark_messages_read(db: AsyncSession, user_id: int, sender_id: int) -> dict:
    result = await db.execute(
        select(Message).where(
            Message.sender_id == sender_id,
            Message.receiver_id == user_id,
            Message.is_read.is_(False),
        )
    )
    for msg in result.scalars().all():
        msg.is_read = True
    await db.flush()
    return {"status": "ok"}
