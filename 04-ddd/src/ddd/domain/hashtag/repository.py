from __future__ import annotations

from abc import ABC, abstractmethod

from ddd.domain.hashtag.entity import Hashtag
from ddd.domain.post.aggregate import PostAggregate


class HashtagRepository(ABC):
    @abstractmethod
    async def get_or_create(self, name: str) -> Hashtag: ...

    @abstractmethod
    async def link_post(self, post_id: int, hashtag_id: int) -> None: ...

    @abstractmethod
    async def unlink_post(self, post_id: int) -> None: ...

    @abstractmethod
    async def search(self, query: str, limit: int) -> list[Hashtag]: ...

    @abstractmethod
    async def get_posts_by_hashtag(self, tag: str, limit: int, offset: int) -> list[PostAggregate]: ...
