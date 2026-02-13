from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from functional_core.shell.models import Notification


async def get_notifications(
    db: AsyncSession, user_id: int, limit: int = 50, offset: int = 0
) -> list[Notification]:
    result = await db.execute(
        select(Notification)
        .where(Notification.user_id == user_id)
        .order_by(Notification.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return list(result.scalars().all())


async def mark_notification_read(db: AsyncSession, notification_id: int, user_id: int) -> dict:
    await db.execute(
        update(Notification)
        .where(Notification.id == notification_id, Notification.user_id == user_id)
        .values(is_read=True)
    )
    await db.flush()
    return {"status": "ok"}


async def mark_all_notifications_read(db: AsyncSession, user_id: int) -> dict:
    await db.execute(
        update(Notification)
        .where(Notification.user_id == user_id, Notification.is_read.is_(False))
        .values(is_read=True)
    )
    await db.flush()
    return {"status": "ok"}
