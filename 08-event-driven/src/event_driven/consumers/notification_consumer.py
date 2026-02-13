from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from event_driven.models.tables import Notification, User


async def on_post_liked(event_data: dict) -> None:
    db: AsyncSession = event_data["db"]
    user_id = event_data["post_author_id"]
    actor_id = event_data["user_id"]

    if user_id == actor_id:
        return

    actor_result = await db.execute(select(User.username).where(User.id == actor_id))
    actor_username = actor_result.scalar_one_or_none() or "Someone"

    notification = Notification(
        user_id=user_id,
        actor_id=actor_id,
        type="like",
        reference_id=event_data["post_id"],
        message=f"{actor_username} liked your post",
    )
    db.add(notification)
    await db.flush()


async def on_comment_added(event_data: dict) -> None:
    db: AsyncSession = event_data["db"]
    user_id = event_data["post_author_id"]
    actor_id = event_data["author_id"]

    if user_id == actor_id:
        return

    actor_result = await db.execute(select(User.username).where(User.id == actor_id))
    actor_username = actor_result.scalar_one_or_none() or "Someone"

    notification = Notification(
        user_id=user_id,
        actor_id=actor_id,
        type="comment",
        reference_id=event_data["post_id"],
        message=f"{actor_username} commented on your post",
    )
    db.add(notification)
    await db.flush()


async def on_user_followed(event_data: dict) -> None:
    db: AsyncSession = event_data["db"]
    user_id = event_data["following_id"]
    actor_id = event_data["follower_id"]

    actor_result = await db.execute(select(User.username).where(User.id == actor_id))
    actor_username = actor_result.scalar_one_or_none() or "Someone"

    notification = Notification(
        user_id=user_id,
        actor_id=actor_id,
        type="follow",
        reference_id=actor_id,
        message=f"{actor_username} started following you",
    )
    db.add(notification)
    await db.flush()
