from __future__ import annotations

from ddd.application.post.service import PostApplicationService
from ddd.domain.hashtag.repository import HashtagRepository
from ddd.domain.post.repository import CommentRepository, LikeRepository, PostRepository
from ddd.domain.social.repository import FollowRepository
from ddd.domain.user.repository import UserRepository


class FeedApplicationService:
    def __init__(
        self,
        post_repo: PostRepository,
        follow_repo: FollowRepository,
        user_repo: UserRepository,
        like_repo: LikeRepository,
        comment_repo: CommentRepository,
    ):
        self.post_service = PostApplicationService(
            post_repo, user_repo, like_repo, comment_repo, None
        )
        self.post_repo = post_repo
        self.follow_repo = follow_repo

    async def get_feed(
        self, user_id: int, limit: int = 20, offset: int = 0
    ) -> list[dict]:
        following_ids = await self.follow_repo.get_following(user_id)
        following_ids.append(user_id)
        posts = await self.post_repo.get_feed(following_ids, limit, offset)
        return [await self.post_service._enrich(p) for p in posts]
