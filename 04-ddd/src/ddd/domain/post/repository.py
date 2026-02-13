from __future__ import annotations

from abc import ABC, abstractmethod

from ddd.domain.post.aggregate import PostAggregate
from ddd.domain.post.entities import Comment, Like


class PostRepository(ABC):
    @abstractmethod
    async def create(self, post: PostAggregate) -> PostAggregate: ...

    @abstractmethod
    async def get_by_id(self, post_id: int) -> PostAggregate | None: ...

    @abstractmethod
    async def get_by_author(self, author_id: int, limit: int, offset: int) -> list[PostAggregate]: ...

    @abstractmethod
    async def get_feed(self, following_ids: list[int], limit: int, offset: int) -> list[PostAggregate]: ...

    @abstractmethod
    async def delete(self, post_id: int) -> None: ...

    @abstractmethod
    async def count_by_author(self, author_id: int) -> int: ...


class CommentRepository(ABC):
    @abstractmethod
    async def create(self, comment: Comment) -> Comment: ...

    @abstractmethod
    async def get_by_id(self, comment_id: int) -> Comment | None: ...

    @abstractmethod
    async def get_by_post(self, post_id: int, limit: int, offset: int) -> list[Comment]: ...

    @abstractmethod
    async def delete(self, comment_id: int) -> None: ...


class LikeRepository(ABC):
    @abstractmethod
    async def create(self, like: Like) -> Like: ...

    @abstractmethod
    async def get(self, post_id: int, user_id: int) -> Like | None: ...

    @abstractmethod
    async def delete(self, post_id: int, user_id: int) -> None: ...

    @abstractmethod
    async def count_by_post(self, post_id: int) -> int: ...
