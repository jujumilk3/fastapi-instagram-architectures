from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from vertical_slice.models.tables import Notification


@dataclass
class GetNotificationsRequest:
    user_id: int
    limit: int
    offset: int
    db: AsyncSession


@dataclass
class NotificationItem:
    id: int
    user_id: int
    actor_id: int
    type: str
    reference_id: int | None
    message: str
    is_read: bool
    created_at: datetime


async def get_notifications_handler(request: GetNotificationsRequest) -> list[NotificationItem]:
    db = request.db
    result = await db.execute(
        select(Notification)
        .where(Notification.user_id == request.user_id)
        .order_by(Notification.created_at.desc())
        .limit(request.limit)
        .offset(request.offset)
    )
    return [
        NotificationItem(
            id=n.id, user_id=n.user_id, actor_id=n.actor_id,
            type=n.type, reference_id=n.reference_id,
            message=n.message, is_read=n.is_read,
            created_at=n.created_at,
        )
        for n in result.scalars().all()
    ]
