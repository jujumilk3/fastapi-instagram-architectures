from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from event_driven.events.definitions import ALL_NOTIFICATIONS_READ, MESSAGE_SENT, MESSAGES_READ, NOTIFICATION_READ
from event_driven.models.tables import Message, Notification
from event_driven.shared.event_broker import broker


async def send_message(
    sender_id: int,
    receiver_id: int,
    content: str,
    db: AsyncSession,
) -> dict:
    message = Message(sender_id=sender_id, receiver_id=receiver_id, content=content)
    db.add(message)
    await db.flush()

    await broker.publish(MESSAGE_SENT, {
        "message_id": message.id,
        "sender_id": sender_id,
        "receiver_id": receiver_id,
        "db": db,
    })

    return {
        "id": message.id,
        "sender_id": message.sender_id,
        "receiver_id": message.receiver_id,
        "content": message.content,
        "is_read": message.is_read,
        "created_at": message.created_at,
    }


async def mark_messages_read(user_id: int, sender_id: int, db: AsyncSession) -> dict:
    await db.execute(
        update(Message)
        .where(Message.sender_id == sender_id, Message.receiver_id == user_id, Message.is_read == False)
        .values(is_read=True)
    )
    await db.flush()

    await broker.publish(MESSAGES_READ, {"user_id": user_id, "sender_id": sender_id, "db": db})

    return {"status": "ok"}


async def mark_notification_read(notification_id: int, user_id: int, db: AsyncSession) -> dict:
    result = await db.execute(
        select(Notification).where(Notification.id == notification_id, Notification.user_id == user_id)
    )
    notif = result.scalar_one_or_none()
    if notif:
        notif.is_read = True
        await db.flush()

    await broker.publish(NOTIFICATION_READ, {"notification_id": notification_id, "user_id": user_id, "db": db})

    return {"status": "ok"}


async def mark_all_notifications_read(user_id: int, db: AsyncSession) -> dict:
    await db.execute(
        update(Notification)
        .where(Notification.user_id == user_id, Notification.is_read == False)
        .values(is_read=True)
    )
    await db.flush()

    await broker.publish(ALL_NOTIFICATIONS_READ, {"user_id": user_id, "db": db})

    return {"status": "ok"}
