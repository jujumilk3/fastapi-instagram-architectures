from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from modular_monolith.modules.auth.models import User
from modular_monolith.modules.follow.models import Follow
from modular_monolith.modules.post.models import Post
from modular_monolith.modules.user.schemas import UserProfileResponse, UserResponse, UserUpdate


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_profile(self, user_id: int) -> UserProfileResponse:
        user = await self.db.get(User, user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        post_count = (await self.db.execute(
            select(func.count()).select_from(Post).where(Post.author_id == user_id)
        )).scalar_one()
        follower_count = (await self.db.execute(
            select(func.count()).select_from(Follow).where(Follow.following_id == user_id)
        )).scalar_one()
        following_count = (await self.db.execute(
            select(func.count()).select_from(Follow).where(Follow.follower_id == user_id)
        )).scalar_one()

        return UserProfileResponse(
            id=user.id, username=user.username, full_name=user.full_name,
            bio=user.bio, profile_image_url=user.profile_image_url,
            post_count=post_count, follower_count=follower_count, following_count=following_count,
        )

    async def update_me(self, user_id: int, data: UserUpdate) -> UserResponse:
        user = await self.db.get(User, user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(user, key, value)
        await self.db.flush()
        await self.db.refresh(user)
        return UserResponse.model_validate(user)

    async def get_followers(self, user_id: int) -> list[UserResponse]:
        result = await self.db.execute(
            select(User).join(Follow, Follow.follower_id == User.id).where(Follow.following_id == user_id)
        )
        return [UserResponse.model_validate(u) for u in result.scalars().all()]

    async def get_following(self, user_id: int) -> list[UserResponse]:
        result = await self.db.execute(
            select(User).join(Follow, Follow.following_id == User.id).where(Follow.follower_id == user_id)
        )
        return [UserResponse.model_validate(u) for u in result.scalars().all()]

    async def search_users(self, query: str, limit: int = 20) -> list[UserResponse]:
        result = await self.db.execute(
            select(User).where(User.username.ilike(f"%{query}%")).limit(limit)
        )
        return [UserResponse.model_validate(u) for u in result.scalars().all()]
