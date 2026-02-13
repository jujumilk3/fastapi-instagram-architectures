from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from event_driven.events.definitions import STORY_CREATED, STORY_DELETED
from event_driven.models.tables import Story, User
from event_driven.shared.event_broker import broker


async def create_story(
    author_id: int,
    image_url: str | None,
    content: str | None,
    db: AsyncSession,
) -> dict:
    user_result = await db.execute(select(User).where(User.id == author_id))
    user = user_result.scalar_one_or_none()

    story = Story(author_id=author_id, image_url=image_url, content=content)
    db.add(story)
    await db.flush()

    await broker.publish(STORY_CREATED, {
        "story_id": story.id,
        "author_id": author_id,
        "db": db,
    })

    return {
        "id": story.id,
        "author_id": story.author_id,
        "author_username": user.username if user else None,
        "image_url": story.image_url,
        "content": story.content,
        "created_at": story.created_at,
    }


async def delete_story(story_id: int, user_id: int, db: AsyncSession) -> None:
    result = await db.execute(select(Story).where(Story.id == story_id))
    story = result.scalar_one_or_none()
    if not story:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Story not found")
    if story.author_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your story")

    await db.delete(story)
    await db.flush()

    await broker.publish(STORY_DELETED, {"story_id": story_id, "author_id": user_id, "db": db})
