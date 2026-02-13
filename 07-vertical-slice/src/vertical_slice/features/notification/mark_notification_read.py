from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from vertical_slice.models.tables import Notification


@dataclass
class MarkNotificationReadRequest:
    notification_id: int
    user_id: int
    db: AsyncSession


async def mark_notification_read_handler(request: MarkNotificationReadRequest) -> dict:
    db = request.db
    await db.execute(
        update(Notification)
        .where(Notification.id == request.notification_id, Notification.user_id == request.user_id)
        .values(is_read=True)
    )
    await db.flush()
    return {"status": "ok"}
