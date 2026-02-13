from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from saga_choreography.models.tables import Notification, User


async def create_notification(
    user_id: int,
    actor_id: int,
    type: str,
    reference_id: int | None,
    message: str,
    db: AsyncSession,
) -> Notification:
    notification = Notification(
        user_id=user_id,
        actor_id=actor_id,
        type=type,
        reference_id=reference_id,
        message=message,
    )
    db.add(notification)
    await db.flush()
    return notification


async def delete_notification_by_id(notification_id: int, db: AsyncSession) -> None:
    result = await db.execute(select(Notification).where(Notification.id == notification_id))
    notif = result.scalar_one_or_none()
    if notif:
        await db.delete(notif)
        await db.flush()


async def get_notifications(
    user_id: int, limit: int, offset: int, db: AsyncSession
) -> list[dict]:
    result = await db.execute(
        select(Notification)
        .where(Notification.user_id == user_id)
        .order_by(Notification.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    notifications = result.scalars().all()
    return [
        {
            "id": n.id,
            "user_id": n.user_id,
            "actor_id": n.actor_id,
            "type": n.type,
            "reference_id": n.reference_id,
            "message": n.message,
            "is_read": n.is_read,
            "created_at": n.created_at,
        }
        for n in notifications
    ]


async def mark_notification_read(notification_id: int, user_id: int, db: AsyncSession) -> dict:
    result = await db.execute(
        select(Notification).where(Notification.id == notification_id, Notification.user_id == user_id)
    )
    notif = result.scalar_one_or_none()
    if notif:
        notif.is_read = True
        await db.flush()
    return {"status": "ok"}


async def mark_all_notifications_read(user_id: int, db: AsyncSession) -> dict:
    await db.execute(
        update(Notification)
        .where(Notification.user_id == user_id, Notification.is_read == False)
        .values(is_read=True)
    )
    await db.flush()
    return {"status": "ok"}
