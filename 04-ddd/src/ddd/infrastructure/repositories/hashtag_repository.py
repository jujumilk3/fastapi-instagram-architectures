from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ddd.domain.hashtag.entity import Hashtag
from ddd.domain.hashtag.repository import HashtagRepository
from ddd.domain.post.aggregate import PostAggregate
from ddd.infrastructure.orm.mapper import hashtag_model_to_entity, post_model_to_aggregate
from ddd.infrastructure.orm.models import HashtagModel, PostHashtagModel, PostModel


class SqlAlchemyHashtagRepository(HashtagRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_or_create(self, name: str) -> Hashtag:
        r = await self.db.execute(
            select(HashtagModel).where(HashtagModel.name == name)
        )
        m = r.scalar_one_or_none()
        if not m:
            m = HashtagModel(name=name)
            self.db.add(m)
            await self.db.flush()
            await self.db.refresh(m)
        return hashtag_model_to_entity(m)

    async def link_post(self, post_id: int, hashtag_id: int) -> None:
        r = await self.db.execute(
            select(PostHashtagModel).where(
                PostHashtagModel.post_id == post_id,
                PostHashtagModel.hashtag_id == hashtag_id,
            )
        )
        if not r.scalar_one_or_none():
            self.db.add(PostHashtagModel(post_id=post_id, hashtag_id=hashtag_id))
            await self.db.flush()

    async def unlink_post(self, post_id: int) -> None:
        r = await self.db.execute(
            select(PostHashtagModel).where(PostHashtagModel.post_id == post_id)
        )
        for m in r.scalars().all():
            await self.db.delete(m)
        await self.db.flush()

    async def search(self, query: str, limit: int) -> list[Hashtag]:
        r = await self.db.execute(
            select(HashtagModel)
            .where(HashtagModel.name.ilike(f"%{query}%"))
            .limit(limit)
        )
        return [hashtag_model_to_entity(m) for m in r.scalars().all()]

    async def get_posts_by_hashtag(
        self, tag: str, limit: int, offset: int
    ) -> list[PostAggregate]:
        r = await self.db.execute(
            select(PostModel)
            .join(PostHashtagModel, PostModel.id == PostHashtagModel.post_id)
            .join(HashtagModel, PostHashtagModel.hashtag_id == HashtagModel.id)
            .where(HashtagModel.name == tag)
            .order_by(PostModel.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return [post_model_to_aggregate(m) for m in r.scalars().all()]
