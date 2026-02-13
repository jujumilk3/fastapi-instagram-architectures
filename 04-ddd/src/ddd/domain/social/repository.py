from __future__ import annotations

from abc import ABC, abstractmethod

from ddd.domain.social.aggregate import Follow, Story


class FollowRepository(ABC):
    @abstractmethod
    async def create(self, follow: Follow) -> Follow: ...

    @abstractmethod
    async def get(self, follower_id: int, following_id: int) -> Follow | None: ...

    @abstractmethod
    async def delete(self, follower_id: int, following_id: int) -> None: ...

    @abstractmethod
    async def get_followers(self, user_id: int) -> list[int]: ...

    @abstractmethod
    async def get_following(self, user_id: int) -> list[int]: ...

    @abstractmethod
    async def count_followers(self, user_id: int) -> int: ...

    @abstractmethod
    async def count_following(self, user_id: int) -> int: ...


class StoryRepository(ABC):
    @abstractmethod
    async def create(self, story: Story) -> Story: ...

    @abstractmethod
    async def get_by_id(self, story_id: int) -> Story | None: ...

    @abstractmethod
    async def get_active_by_author(self, author_id: int) -> list[Story]: ...

    @abstractmethod
    async def get_feed(self, following_ids: list[int]) -> list[Story]: ...

    @abstractmethod
    async def delete(self, story_id: int) -> None: ...
