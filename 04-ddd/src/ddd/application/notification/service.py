from __future__ import annotations

from ddd.domain.notification.entity import Notification
from ddd.domain.notification.repository import NotificationRepository


class NotificationApplicationService:
    def __init__(self, notification_repo: NotificationRepository):
        self.notification_repo = notification_repo

    async def get_notifications(
        self, user_id: int, limit: int, offset: int
    ) -> list[Notification]:
        return await self.notification_repo.get_by_user(user_id, limit, offset)

    async def mark_read(self, notification_id: int, user_id: int) -> dict:
        await self.notification_repo.mark_read(notification_id, user_id)
        return {"status": "ok"}

    async def mark_all_read(self, user_id: int) -> dict:
        await self.notification_repo.mark_all_read(user_id)
        return {"status": "ok"}
