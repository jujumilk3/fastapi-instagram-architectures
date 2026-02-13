from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from layered.repositories.follow import FollowRepository
from layered.repositories.post import PostRepository
from layered.repositories.user import UserRepository
from layered.schemas.user import UserProfileResponse, UserResponse, UserUpdate


class UserService:
    def __init__(self, db: AsyncSession):
        self.user_repo = UserRepository(db)
        self.follow_repo = FollowRepository(db)
        self.post_repo = PostRepository(db)

    async def get_profile(self, user_id: int) -> UserProfileResponse:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        post_count = await self.post_repo.count_by_author(user_id)
        follower_count = await self.follow_repo.count_followers(user_id)
        following_count = await self.follow_repo.count_following(user_id)

        return UserProfileResponse(
            id=user.id,
            username=user.username,
            full_name=user.full_name,
            bio=user.bio,
            profile_image_url=user.profile_image_url,
            post_count=post_count,
            follower_count=follower_count,
            following_count=following_count,
        )

    async def update_me(self, user_id: int, data: UserUpdate) -> UserResponse:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(user, key, value)

        user = await self.user_repo.update(user)
        return UserResponse.model_validate(user)

    async def get_followers(self, user_id: int) -> list[UserResponse]:
        follower_ids = await self.follow_repo.get_followers(user_id)
        users = []
        for fid in follower_ids:
            user = await self.user_repo.get_by_id(fid)
            if user:
                users.append(UserResponse.model_validate(user))
        return users

    async def get_following(self, user_id: int) -> list[UserResponse]:
        following_ids = await self.follow_repo.get_following(user_id)
        users = []
        for fid in following_ids:
            user = await self.user_repo.get_by_id(fid)
            if user:
                users.append(UserResponse.model_validate(user))
        return users
