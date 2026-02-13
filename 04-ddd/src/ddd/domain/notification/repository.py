from __future__ import annotations

from abc import ABC, abstractmethod

from ddd.domain.notification.entity import Notification


class NotificationRepository(ABC):
    @abstractmethod
    async def create(self, notification: Notification) -> Notification: ...

    @abstractmethod
    async def get_by_user(self, user_id: int, limit: int, offset: int) -> list[Notification]: ...

    @abstractmethod
    async def mark_read(self, notification_id: int, user_id: int) -> None: ...

    @abstractmethod
    async def mark_all_read(self, user_id: int) -> None: ...
