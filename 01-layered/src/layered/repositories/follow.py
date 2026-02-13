from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from layered.models.follow import Follow


class FollowRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, follow: Follow) -> Follow:
        self.db.add(follow)
        await self.db.flush()
        return follow

    async def get(self, follower_id: int, following_id: int) -> Follow | None:
        result = await self.db.execute(
            select(Follow).where(
                Follow.follower_id == follower_id,
                Follow.following_id == following_id,
            )
        )
        return result.scalar_one_or_none()

    async def delete(self, follow: Follow) -> None:
        await self.db.delete(follow)
        await self.db.flush()

    async def get_followers(self, user_id: int) -> list[int]:
        result = await self.db.execute(
            select(Follow.follower_id).where(Follow.following_id == user_id)
        )
        return list(result.scalars().all())

    async def get_following(self, user_id: int) -> list[int]:
        result = await self.db.execute(
            select(Follow.following_id).where(Follow.follower_id == user_id)
        )
        return list(result.scalars().all())

    async def count_followers(self, user_id: int) -> int:
        result = await self.db.execute(
            select(func.count()).select_from(Follow).where(Follow.following_id == user_id)
        )
        return result.scalar_one()

    async def count_following(self, user_id: int) -> int:
        result = await self.db.execute(
            select(func.count()).select_from(Follow).where(Follow.follower_id == user_id)
        )
        return result.scalar_one()
