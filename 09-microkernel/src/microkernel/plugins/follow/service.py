from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from microkernel.plugins.auth.models import User
from microkernel.plugins.follow.models import Follow
from microkernel.plugins.notification.service import NotificationService


class FollowService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def follow(self, follower_id: int, following_id: int) -> dict:
        if follower_id == following_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot follow yourself")

        target = await self.db.get(User, following_id)
        if not target:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        result = await self.db.execute(
            select(Follow).where(Follow.follower_id == follower_id, Follow.following_id == following_id)
        )
        if result.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Already following")

        self.db.add(Follow(follower_id=follower_id, following_id=following_id))
        await self.db.flush()

        await NotificationService(self.db).create_notification(
            user_id=following_id, actor_id=follower_id,
            type="follow", message="started following you",
        )
        return {"following": True}

    async def unfollow(self, follower_id: int, following_id: int) -> dict:
        result = await self.db.execute(
            select(Follow).where(Follow.follower_id == follower_id, Follow.following_id == following_id)
        )
        existing = result.scalar_one_or_none()
        if not existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not following")
        await self.db.delete(existing)
        await self.db.flush()
        return {"following": False}
