from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from microkernel.plugins.notification.models import Notification
from microkernel.plugins.notification.schemas import NotificationResponse


class NotificationService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_notification(
        self, user_id: int, actor_id: int, type: str, message: str, reference_id: int | None = None,
    ) -> None:
        self.db.add(Notification(
            user_id=user_id, actor_id=actor_id, type=type,
            reference_id=reference_id, message=message,
        ))
        await self.db.flush()

    async def get_notifications(self, user_id: int, limit: int = 50, offset: int = 0) -> list[NotificationResponse]:
        result = await self.db.execute(
            select(Notification).where(Notification.user_id == user_id).order_by(Notification.created_at.desc()).limit(limit).offset(offset)
        )
        return [NotificationResponse.model_validate(n) for n in result.scalars().all()]

    async def mark_read(self, notification_id: int, user_id: int) -> dict:
        await self.db.execute(
            update(Notification).where(Notification.id == notification_id, Notification.user_id == user_id).values(is_read=True)
        )
        await self.db.flush()
        return {"status": "ok"}

    async def mark_all_read(self, user_id: int) -> dict:
        await self.db.execute(
            update(Notification).where(Notification.user_id == user_id, Notification.is_read.is_(False)).values(is_read=True)
        )
        await self.db.flush()
        return {"status": "ok"}
