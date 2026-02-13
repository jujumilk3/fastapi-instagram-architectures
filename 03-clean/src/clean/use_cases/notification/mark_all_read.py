from clean.use_cases.interfaces.repositories import NotificationRepository


class MarkAllNotificationsReadUseCase:
    def __init__(self, notification_repo: NotificationRepository):
        self.notification_repo = notification_repo

    async def execute(self, user_id: int) -> dict:
        await self.notification_repo.mark_all_read(user_id)
        return {"status": "ok"}
