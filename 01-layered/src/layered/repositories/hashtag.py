from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from layered.models.hashtag import Hashtag, PostHashtag
from layered.models.post import Post


class HashtagRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_or_create(self, name: str) -> Hashtag:
        result = await self.db.execute(select(Hashtag).where(Hashtag.name == name))
        hashtag = result.scalar_one_or_none()
        if not hashtag:
            hashtag = Hashtag(name=name)
            self.db.add(hashtag)
            await self.db.flush()
            await self.db.refresh(hashtag)
        return hashtag

    async def link_post(self, post_id: int, hashtag_id: int) -> None:
        existing = await self.db.execute(
            select(PostHashtag).where(
                PostHashtag.post_id == post_id, PostHashtag.hashtag_id == hashtag_id
            )
        )
        if not existing.scalar_one_or_none():
            self.db.add(PostHashtag(post_id=post_id, hashtag_id=hashtag_id))
            await self.db.flush()

    async def unlink_post(self, post_id: int) -> None:
        result = await self.db.execute(
            select(PostHashtag).where(PostHashtag.post_id == post_id)
        )
        for ph in result.scalars().all():
            await self.db.delete(ph)
        await self.db.flush()

    async def search(self, query: str, limit: int = 20) -> list[Hashtag]:
        result = await self.db.execute(
            select(Hashtag).where(Hashtag.name.ilike(f"%{query}%")).limit(limit)
        )
        return list(result.scalars().all())

    async def get_posts_by_hashtag(self, tag: str, limit: int = 20, offset: int = 0) -> list[Post]:
        result = await self.db.execute(
            select(Post)
            .join(PostHashtag, Post.id == PostHashtag.post_id)
            .join(Hashtag, PostHashtag.hashtag_id == Hashtag.id)
            .options(selectinload(Post.author), selectinload(Post.likes), selectinload(Post.comments))
            .where(Hashtag.name == tag)
            .order_by(Post.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
