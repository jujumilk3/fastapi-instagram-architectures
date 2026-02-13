from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from layered.models.follow import Follow
from layered.models.notification import Notification
from layered.repositories.follow import FollowRepository
from layered.repositories.notification import NotificationRepository
from layered.repositories.user import UserRepository


class FollowService:
    def __init__(self, db: AsyncSession):
        self.follow_repo = FollowRepository(db)
        self.user_repo = UserRepository(db)
        self.notification_repo = NotificationRepository(db)

    async def follow(self, follower_id: int, following_id: int) -> dict:
        if follower_id == following_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot follow yourself")

        target = await self.user_repo.get_by_id(following_id)
        if not target:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        existing = await self.follow_repo.get(follower_id, following_id)
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Already following")

        await self.follow_repo.create(Follow(follower_id=follower_id, following_id=following_id))

        await self.notification_repo.create(
            Notification(
                user_id=following_id,
                actor_id=follower_id,
                type="follow",
                message="started following you",
            )
        )

        return {"following": True}

    async def unfollow(self, follower_id: int, following_id: int) -> dict:
        existing = await self.follow_repo.get(follower_id, following_id)
        if not existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not following")
        await self.follow_repo.delete(existing)
        return {"following": False}
