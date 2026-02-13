from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ddd.domain.social.aggregate import Follow, Story
from ddd.domain.social.repository import FollowRepository, StoryRepository
from ddd.infrastructure.orm.mapper import follow_model_to_entity, story_model_to_entity
from ddd.infrastructure.orm.models import FollowModel, StoryModel


class SqlAlchemyFollowRepository(FollowRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, follow: Follow) -> Follow:
        m = FollowModel(
            follower_id=follow.follower_id, following_id=follow.following_id
        )
        self.db.add(m)
        await self.db.flush()
        await self.db.refresh(m)
        return follow_model_to_entity(m)

    async def get(self, follower_id: int, following_id: int) -> Follow | None:
        r = await self.db.execute(
            select(FollowModel).where(
                FollowModel.follower_id == follower_id,
                FollowModel.following_id == following_id,
            )
        )
        m = r.scalar_one_or_none()
        return follow_model_to_entity(m) if m else None

    async def delete(self, follower_id: int, following_id: int) -> None:
        r = await self.db.execute(
            select(FollowModel).where(
                FollowModel.follower_id == follower_id,
                FollowModel.following_id == following_id,
            )
        )
        m = r.scalar_one_or_none()
        if m:
            await self.db.delete(m)
            await self.db.flush()

    async def get_followers(self, user_id: int) -> list[int]:
        r = await self.db.execute(
            select(FollowModel.follower_id).where(
                FollowModel.following_id == user_id
            )
        )
        return list(r.scalars().all())

    async def get_following(self, user_id: int) -> list[int]:
        r = await self.db.execute(
            select(FollowModel.following_id).where(
                FollowModel.follower_id == user_id
            )
        )
        return list(r.scalars().all())

    async def count_followers(self, user_id: int) -> int:
        r = await self.db.execute(
            select(func.count())
            .select_from(FollowModel)
            .where(FollowModel.following_id == user_id)
        )
        return r.scalar_one()

    async def count_following(self, user_id: int) -> int:
        r = await self.db.execute(
            select(func.count())
            .select_from(FollowModel)
            .where(FollowModel.follower_id == user_id)
        )
        return r.scalar_one()


class SqlAlchemyStoryRepository(StoryRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, story: Story) -> Story:
        m = StoryModel(
            author_id=story.author_id,
            image_url=story.image_url,
            content=story.content,
        )
        self.db.add(m)
        await self.db.flush()
        await self.db.refresh(m)
        return story_model_to_entity(m)

    async def get_by_id(self, story_id: int) -> Story | None:
        m = await self.db.get(StoryModel, story_id)
        return story_model_to_entity(m) if m else None

    async def get_active_by_author(self, author_id: int) -> list[Story]:
        cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
        r = await self.db.execute(
            select(StoryModel)
            .where(
                StoryModel.author_id == author_id,
                StoryModel.created_at >= cutoff,
            )
            .order_by(StoryModel.created_at.desc())
        )
        return [story_model_to_entity(m) for m in r.scalars().all()]

    async def get_feed(self, following_ids: list[int]) -> list[Story]:
        cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
        r = await self.db.execute(
            select(StoryModel)
            .where(
                StoryModel.author_id.in_(following_ids),
                StoryModel.created_at >= cutoff,
            )
            .order_by(StoryModel.created_at.desc())
        )
        return [story_model_to_entity(m) for m in r.scalars().all()]

    async def delete(self, story_id: int) -> None:
        m = await self.db.get(StoryModel, story_id)
        if m:
            await self.db.delete(m)
            await self.db.flush()
