from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from vertical_slice.models.tables import Story


@dataclass
class CreateStoryRequest:
    author_id: int
    image_url: str | None
    content: str | None
    db: AsyncSession


@dataclass
class CreateStoryResponse:
    id: int
    author_id: int
    author_username: str | None
    image_url: str | None
    content: str | None
    created_at: datetime


async def create_story_handler(request: CreateStoryRequest) -> CreateStoryResponse:
    db = request.db
    story = Story(author_id=request.author_id, image_url=request.image_url, content=request.content)
    db.add(story)
    await db.flush()
    await db.refresh(story)

    return CreateStoryResponse(
        id=story.id,
        author_id=story.author_id,
        author_username=None,
        image_url=story.image_url,
        content=story.content,
        created_at=story.created_at,
    )
