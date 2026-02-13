from __future__ import annotations

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from ddd.domain.notification.entity import Notification
from ddd.domain.notification.repository import NotificationRepository
from ddd.infrastructure.orm.mapper import notification_model_to_entity
from ddd.infrastructure.orm.models import NotificationModel


class SqlAlchemyNotificationRepository(NotificationRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, notification: Notification) -> Notification:
        m = NotificationModel(
            user_id=notification.user_id,
            actor_id=notification.actor_id,
            type=notification.type,
            reference_id=notification.reference_id,
            message=notification.message,
        )
        self.db.add(m)
        await self.db.flush()
        await self.db.refresh(m)
        return notification_model_to_entity(m)

    async def get_by_user(
        self, user_id: int, limit: int, offset: int
    ) -> list[Notification]:
        r = await self.db.execute(
            select(NotificationModel)
            .where(NotificationModel.user_id == user_id)
            .order_by(NotificationModel.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return [notification_model_to_entity(m) for m in r.scalars().all()]

    async def mark_read(self, notification_id: int, user_id: int) -> None:
        await self.db.execute(
            update(NotificationModel)
            .where(
                NotificationModel.id == notification_id,
                NotificationModel.user_id == user_id,
            )
            .values(is_read=True)
        )
        await self.db.flush()

    async def mark_all_read(self, user_id: int) -> None:
        await self.db.execute(
            update(NotificationModel)
            .where(
                NotificationModel.user_id == user_id,
                NotificationModel.is_read.is_(False),
            )
            .values(is_read=True)
        )
        await self.db.flush()
