from sqlalchemy.ext.asyncio import AsyncSession

from layered.repositories.notification import NotificationRepository
from layered.schemas.notification import NotificationResponse


class NotificationService:
    def __init__(self, db: AsyncSession):
        self.notification_repo = NotificationRepository(db)

    async def get_notifications(self, user_id: int, limit: int = 50, offset: int = 0) -> list[NotificationResponse]:
        notifications = await self.notification_repo.get_by_user(user_id, limit, offset)
        return [NotificationResponse.model_validate(n) for n in notifications]

    async def mark_read(self, notification_id: int, user_id: int) -> dict:
        await self.notification_repo.mark_read(notification_id, user_id)
        return {"status": "ok"}

    async def mark_all_read(self, user_id: int) -> dict:
        await self.notification_repo.mark_all_read(user_id)
        return {"status": "ok"}
