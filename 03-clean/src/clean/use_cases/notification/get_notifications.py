from clean.entities.social import Notification
from clean.use_cases.interfaces.repositories import NotificationRepository


class GetNotificationsUseCase:
    def __init__(self, notification_repo: NotificationRepository):
        self.notification_repo = notification_repo

    async def execute(self, user_id: int, limit: int, offset: int) -> list[Notification]:
        return await self.notification_repo.get_by_user(user_id, limit, offset)
