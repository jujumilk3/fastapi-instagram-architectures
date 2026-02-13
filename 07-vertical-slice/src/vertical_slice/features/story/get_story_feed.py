from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from vertical_slice.models.tables import Follow, Story, User

STORY_EXPIRY_HOURS = 24


@dataclass
class GetStoryFeedRequest:
    user_id: int
    db: AsyncSession


@dataclass
class StoryItem:
    id: int
    author_id: int
    author_username: str | None
    image_url: str | None
    content: str | None
    created_at: datetime


async def get_story_feed_handler(request: GetStoryFeedRequest) -> list[StoryItem]:
    db = request.db
    result = await db.execute(select(Follow.following_id).where(Follow.follower_id == request.user_id))
    following_ids = list(result.scalars().all())
    following_ids.append(request.user_id)

    cutoff = datetime.now(timezone.utc) - timedelta(hours=STORY_EXPIRY_HOURS)
    result = await db.execute(
        select(Story)
        .where(Story.author_id.in_(following_ids), Story.created_at >= cutoff)
        .order_by(Story.created_at.desc())
    )
    stories = []
    for s in result.scalars().all():
        user = await db.get(User, s.author_id)
        stories.append(StoryItem(
            id=s.id,
            author_id=s.author_id,
            author_username=user.username if user else None,
            image_url=s.image_url,
            content=s.content,
            created_at=s.created_at,
        ))
    return stories
