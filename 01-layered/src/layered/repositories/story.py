from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from layered.models.story import Story

STORY_EXPIRY_HOURS = 24


class StoryRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, story: Story) -> Story:
        self.db.add(story)
        await self.db.flush()
        await self.db.refresh(story)
        return story

    async def get_by_id(self, story_id: int) -> Story | None:
        return await self.db.get(Story, story_id)

    async def get_active_by_author(self, author_id: int) -> list[Story]:
        cutoff = datetime.now(timezone.utc) - timedelta(hours=STORY_EXPIRY_HOURS)
        result = await self.db.execute(
            select(Story)
            .options(selectinload(Story.author))
            .where(Story.author_id == author_id, Story.created_at >= cutoff)
            .order_by(Story.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_feed(self, following_ids: list[int]) -> list[Story]:
        cutoff = datetime.now(timezone.utc) - timedelta(hours=STORY_EXPIRY_HOURS)
        result = await self.db.execute(
            select(Story)
            .options(selectinload(Story.author))
            .where(Story.author_id.in_(following_ids), Story.created_at >= cutoff)
            .order_by(Story.created_at.desc())
        )
        return list(result.scalars().all())

    async def delete(self, story: Story) -> None:
        await self.db.delete(story)
        await self.db.flush()
