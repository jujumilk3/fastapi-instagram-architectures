from sqlalchemy import or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from saga_choreography.models.tables import Message


async def create_message(
    sender_id: int,
    receiver_id: int,
    content: str,
    db: AsyncSession,
) -> Message:
    message = Message(sender_id=sender_id, receiver_id=receiver_id, content=content)
    db.add(message)
    await db.flush()
    return message


async def delete_message_by_id(message_id: int, db: AsyncSession) -> None:
    result = await db.execute(select(Message).where(Message.id == message_id))
    message = result.scalar_one_or_none()
    if message:
        await db.delete(message)
        await db.flush()


async def mark_messages_read(user_id: int, sender_id: int, db: AsyncSession) -> dict:
    await db.execute(
        update(Message)
        .where(Message.sender_id == sender_id, Message.receiver_id == user_id, Message.is_read == False)
        .values(is_read=True)
    )
    await db.flush()
    return {"status": "ok"}


async def get_conversations(user_id: int, db: AsyncSession) -> list[dict]:
    result = await db.execute(
        select(Message)
        .where(or_(Message.sender_id == user_id, Message.receiver_id == user_id))
        .order_by(Message.created_at.desc())
    )
    messages = result.scalars().all()

    seen: set[int] = set()
    conversations: list[dict] = []
    for msg in messages:
        other_id = msg.receiver_id if msg.sender_id == user_id else msg.sender_id
        if other_id not in seen:
            seen.add(other_id)
            conversations.append({
                "other_user_id": other_id,
                "last_message": {
                    "id": msg.id,
                    "sender_id": msg.sender_id,
                    "receiver_id": msg.receiver_id,
                    "content": msg.content,
                    "is_read": msg.is_read,
                    "created_at": msg.created_at,
                },
            })
    return conversations


async def get_conversation(
    user_id: int, other_user_id: int, limit: int, offset: int, db: AsyncSession
) -> list[dict]:
    result = await db.execute(
        select(Message)
        .where(
            or_(
                (Message.sender_id == user_id) & (Message.receiver_id == other_user_id),
                (Message.sender_id == other_user_id) & (Message.receiver_id == user_id),
            )
        )
        .order_by(Message.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    messages = result.scalars().all()
    return [
        {
            "id": m.id,
            "sender_id": m.sender_id,
            "receiver_id": m.receiver_id,
            "content": m.content,
            "is_read": m.is_read,
            "created_at": m.created_at,
        }
        for m in messages
    ]
