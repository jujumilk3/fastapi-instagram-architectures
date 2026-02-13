from __future__ import annotations

from fastapi import HTTPException, status

from ddd.domain.post.repository import PostRepository
from ddd.domain.social.repository import FollowRepository
from ddd.domain.user.aggregate import UserAggregate
from ddd.domain.user.repository import UserRepository


class UserApplicationService:
    def __init__(
        self,
        user_repo: UserRepository,
        follow_repo: FollowRepository,
        post_repo: PostRepository,
    ):
        self.user_repo = user_repo
        self.follow_repo = follow_repo
        self.post_repo = post_repo

    async def get_profile(self, user_id: int) -> dict:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        return {
            "id": user.id,
            "username": user.username.value,
            "full_name": user.full_name,
            "bio": user.bio,
            "profile_image_url": user.profile_image_url,
            "post_count": await self.post_repo.count_by_author(user_id),
            "follower_count": await self.follow_repo.count_followers(user_id),
            "following_count": await self.follow_repo.count_following(user_id),
        }

    async def update_me(self, user_id: int, **kwargs) -> UserAggregate:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        user.update_profile(**kwargs)
        saved = await self.user_repo.update(user)
        user.collect_events()
        return saved

    async def get_followers(self, user_id: int) -> list[UserAggregate]:
        ids = await self.follow_repo.get_followers(user_id)
        users = []
        for uid in ids:
            u = await self.user_repo.get_by_id(uid)
            if u:
                users.append(u)
        return users

    async def get_following(self, user_id: int) -> list[UserAggregate]:
        ids = await self.follow_repo.get_following(user_id)
        users = []
        for uid in ids:
            u = await self.user_repo.get_by_id(uid)
            if u:
                users.append(u)
        return users
