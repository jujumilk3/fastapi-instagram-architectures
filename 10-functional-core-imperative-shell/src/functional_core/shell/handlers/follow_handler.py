from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from functional_core.core.follow import validate_follow
from functional_core.core.notification import create_notification_data
from functional_core.shell.models import Follow, Notification, User


async def follow_user(db: AsyncSession, follower_id: int, following_id: int) -> dict:
    result = validate_follow(follower_id, following_id)
    if not result.success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result.error)

    target = await db.get(User, following_id)
    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    existing_result = await db.execute(
        select(Follow).where(
            Follow.follower_id == follower_id, Follow.following_id == following_id
        )
    )
    if existing_result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Already following")

    db.add(Follow(follower_id=follower_id, following_id=following_id))

    notif_data = create_notification_data("follow", follower_id, following_id)
    db.add(Notification(**notif_data))

    await db.flush()
    return {"following": True}


async def unfollow_user(db: AsyncSession, follower_id: int, following_id: int) -> dict:
    existing_result = await db.execute(
        select(Follow).where(
            Follow.follower_id == follower_id, Follow.following_id == following_id
        )
    )
    existing = existing_result.scalar_one_or_none()
    if not existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not following")

    await db.delete(existing)
    await db.flush()
    return {"following": False}
