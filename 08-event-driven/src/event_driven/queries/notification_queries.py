from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from event_driven.models.tables import Notification


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
