from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from event_driven.models.tables import Follow, Story, User


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
