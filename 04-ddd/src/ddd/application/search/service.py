from __future__ import annotations

from ddd.domain.hashtag.entity import Hashtag
from ddd.domain.hashtag.repository import HashtagRepository
from ddd.domain.post.repository import CommentRepository, LikeRepository
from ddd.domain.user.aggregate import UserAggregate
from ddd.domain.user.repository import UserRepository


class SearchApplicationService:
    def __init__(
        self,
        user_repo: UserRepository,
        hashtag_repo: HashtagRepository,
        like_repo: LikeRepository,
        comment_repo: CommentRepository,
    ):
        self.user_repo = user_repo
        self.hashtag_repo = hashtag_repo
        self.like_repo = like_repo
        self.comment_repo = comment_repo

    async def search_users(
        self, query: str, limit: int = 20
    ) -> list[UserAggregate]:
        return await self.user_repo.search(query, limit)

    async def search_hashtags(self, query: str, limit: int = 20) -> list[Hashtag]:
        return await self.hashtag_repo.search(query, limit)

    async def get_posts_by_hashtag(
        self, tag: str, limit: int = 20, offset: int = 0
    ) -> list[dict]:
        posts = await self.hashtag_repo.get_posts_by_hashtag(tag, limit, offset)
        result = []
        for p in posts:
            author = await self.user_repo.get_by_id(p.author_id)
            like_count = await self.like_repo.count_by_post(p.id)
            comments = await self.comment_repo.get_by_post(p.id, 0, 0)
            result.append({
                "id": p.id,
                "author_id": p.author_id,
                "author_username": author.username.value if author else None,
                "content": p.content,
                "image_url": p.image_url,
                "like_count": like_count,
                "comment_count": len(comments),
                "created_at": p.created_at,
            })
        return result
