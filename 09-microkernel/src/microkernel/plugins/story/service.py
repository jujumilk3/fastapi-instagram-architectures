from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from microkernel.plugins.auth.models import User
from microkernel.plugins.follow.models import Follow
from microkernel.plugins.story.models import Story
from microkernel.plugins.story.schemas import StoryCreate, StoryResponse

STORY_EXPIRY_HOURS = 24


class StoryService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def _to_response(self, story: Story) -> StoryResponse:
        user = await self.db.get(User, story.author_id)
        return StoryResponse(
            id=story.id, author_id=story.author_id,
            author_username=user.username if user else None,
            image_url=story.image_url, content=story.content,
            created_at=story.created_at,
        )

    async def create(self, author_id: int, data: StoryCreate) -> StoryResponse:
        story = Story(author_id=author_id, image_url=data.image_url, content=data.content)
        self.db.add(story)
        await self.db.flush()
        await self.db.refresh(story)
        return StoryResponse(
            id=story.id, author_id=story.author_id,
            image_url=story.image_url, content=story.content,
            created_at=story.created_at,
        )

    async def get_my_stories(self, user_id: int) -> list[StoryResponse]:
        cutoff = datetime.now(timezone.utc) - timedelta(hours=STORY_EXPIRY_HOURS)
        result = await self.db.execute(
            select(Story).where(Story.author_id == user_id, Story.created_at >= cutoff).order_by(Story.created_at.desc())
        )
        return [await self._to_response(s) for s in result.scalars().all()]

    async def get_feed(self, user_id: int) -> list[StoryResponse]:
        result = await self.db.execute(select(Follow.following_id).where(Follow.follower_id == user_id))
        following_ids = list(result.scalars().all())
        following_ids.append(user_id)

        cutoff = datetime.now(timezone.utc) - timedelta(hours=STORY_EXPIRY_HOURS)
        result = await self.db.execute(
            select(Story).where(Story.author_id.in_(following_ids), Story.created_at >= cutoff).order_by(Story.created_at.desc())
        )
        return [await self._to_response(s) for s in result.scalars().all()]

    async def delete(self, story_id: int, user_id: int) -> None:
        story = await self.db.get(Story, story_id)
        if not story:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Story not found")
        if story.author_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your story")
        await self.db.delete(story)
        await self.db.flush()
