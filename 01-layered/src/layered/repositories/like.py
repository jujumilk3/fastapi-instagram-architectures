from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from layered.models.like import Like


class LikeRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, like: Like) -> Like:
        self.db.add(like)
        await self.db.flush()
        return like

    async def get(self, post_id: int, user_id: int) -> Like | None:
        result = await self.db.execute(
            select(Like).where(Like.post_id == post_id, Like.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def delete(self, like: Like) -> None:
        await self.db.delete(like)
        await self.db.flush()

    async def count_by_post(self, post_id: int) -> int:
        result = await self.db.execute(
            select(func.count()).select_from(Like).where(Like.post_id == post_id)
        )
        return result.scalar_one()
