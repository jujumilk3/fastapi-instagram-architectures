from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from layered.models.post import Post


class PostRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, post: Post) -> Post:
        self.db.add(post)
        await self.db.flush()
        await self.db.refresh(post)
        return post

    async def get_by_id(self, post_id: int) -> Post | None:
        result = await self.db.execute(
            select(Post)
            .options(selectinload(Post.author), selectinload(Post.likes), selectinload(Post.comments))
            .where(Post.id == post_id)
        )
        return result.scalar_one_or_none()

    async def get_by_author(self, author_id: int, limit: int = 20, offset: int = 0) -> list[Post]:
        result = await self.db.execute(
            select(Post)
            .options(selectinload(Post.author), selectinload(Post.likes), selectinload(Post.comments))
            .where(Post.author_id == author_id)
            .order_by(Post.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def get_feed(self, following_ids: list[int], limit: int = 20, offset: int = 0) -> list[Post]:
        result = await self.db.execute(
            select(Post)
            .options(selectinload(Post.author), selectinload(Post.likes), selectinload(Post.comments))
            .where(Post.author_id.in_(following_ids))
            .order_by(Post.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def delete(self, post: Post) -> None:
        await self.db.delete(post)
        await self.db.flush()

    async def count_by_author(self, author_id: int) -> int:
        result = await self.db.execute(
            select(func.count()).select_from(Post).where(Post.author_id == author_id)
        )
        return result.scalar_one()
