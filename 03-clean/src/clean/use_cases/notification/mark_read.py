from clean.use_cases.interfaces.repositories import NotificationRepository


class MarkNotificationReadUseCase:
    def __init__(self, notification_repo: NotificationRepository):
        self.notification_repo = notification_repo

    async def execute(self, notification_id: int, user_id: int) -> dict:
        await self.notification_repo.mark_read(notification_id, user_id)
        return {"status": "ok"}
