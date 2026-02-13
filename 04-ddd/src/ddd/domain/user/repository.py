from __future__ import annotations

from abc import ABC, abstractmethod

from ddd.domain.user.aggregate import UserAggregate


class UserRepository(ABC):
    @abstractmethod
    async def create(self, user: UserAggregate) -> UserAggregate: ...

    @abstractmethod
    async def get_by_id(self, user_id: int) -> UserAggregate | None: ...

    @abstractmethod
    async def get_by_email(self, email: str) -> UserAggregate | None: ...

    @abstractmethod
    async def get_by_username(self, username: str) -> UserAggregate | None: ...

    @abstractmethod
    async def update(self, user: UserAggregate) -> UserAggregate: ...

    @abstractmethod
    async def search(self, query: str, limit: int = 20) -> list[UserAggregate]: ...
