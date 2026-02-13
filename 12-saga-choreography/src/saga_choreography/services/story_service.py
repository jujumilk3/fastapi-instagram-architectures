from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from saga_choreography.models.tables import Follow, Story, User


async def create_story(
    author_id: int,
    image_url: str | None,
    content: str | None,
    db: AsyncSession,
) -> Story:
    story = Story(author_id=author_id, image_url=image_url, content=content)
    db.add(story)
    await db.flush()
    return story


async def delete_story(story_id: int, user_id: int, db: AsyncSession) -> None:
    result = await db.execute(select(Story).where(Story.id == story_id))
    story = result.scalar_one_or_none()
    if not story:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Story not found")
    if story.author_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your story")
    await db.delete(story)
    await db.flush()


async def delete_story_by_id(story_id: int, db: AsyncSession) -> None:
    result = await db.execute(select(Story).where(Story.id == story_id))
    story = result.scalar_one_or_none()
    if story:
        await db.delete(story)
        await db.flush()


async def get_my_stories(user_id: int, db: AsyncSession) -> list[dict]:
    result = await db.execute(
        select(Story, User.username)
        .outerjoin(User, Story.author_id == User.id)
        .where(Story.author_id == user_id)
        .order_by(Story.created_at.desc())
    )
    rows = result.all()
    return [
        {
            "id": story.id,
            "author_id": story.author_id,
            "author_username": username,
            "image_url": story.image_url,
            "content": story.content,
            "created_at": story.created_at,
        }
        for story, username in rows
    ]


async def get_story_feed(user_id: int, db: AsyncSession) -> list[dict]:
    following_result = await db.execute(
        select(Follow.following_id).where(Follow.follower_id == user_id)
    )
    following_ids = [row[0] for row in following_result.all()]
    following_ids.append(user_id)

    result = await db.execute(
        select(Story, User.username)
        .outerjoin(User, Story.author_id == User.id)
        .where(Story.author_id.in_(following_ids))
        .order_by(Story.created_at.desc())
    )
    rows = result.all()
    return [
        {
            "id": story.id,
            "author_id": story.author_id,
            "author_username": username,
            "image_url": story.image_url,
            "content": story.content,
            "created_at": story.created_at,
        }
        for story, username in rows
    ]
