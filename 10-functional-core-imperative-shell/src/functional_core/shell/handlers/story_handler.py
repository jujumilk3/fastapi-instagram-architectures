from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from functional_core.core.story import get_story_cutoff
from functional_core.shell.models import Follow, Story


async def create_story(
    db: AsyncSession, author_id: int, image_url: str | None, content: str | None
) -> Story:
    story = Story(author_id=author_id, image_url=image_url, content=content)
    db.add(story)
    await db.flush()
    await db.refresh(story)
    return story


async def get_my_stories(db: AsyncSession, user_id: int) -> list[Story]:
    cutoff = get_story_cutoff()
    result = await db.execute(
        select(Story)
        .options(selectinload(Story.author))
        .where(Story.author_id == user_id, Story.created_at >= cutoff)
        .order_by(Story.created_at.desc())
    )
    return list(result.scalars().all())


async def get_story_feed(db: AsyncSession, user_id: int) -> list[Story]:
    following_result = await db.execute(
        select(Follow.following_id).where(Follow.follower_id == user_id)
    )
    following_ids = list(following_result.scalars().all())
    following_ids.append(user_id)

    cutoff = get_story_cutoff()
    result = await db.execute(
        select(Story)
        .options(selectinload(Story.author))
        .where(Story.author_id.in_(following_ids), Story.created_at >= cutoff)
        .order_by(Story.created_at.desc())
    )
    return list(result.scalars().all())


async def delete_story(db: AsyncSession, story_id: int, user_id: int) -> None:
    story = await db.get(Story, story_id)
    if not story:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Story not found")
    if story.author_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your story")
    await db.delete(story)
    await db.flush()
