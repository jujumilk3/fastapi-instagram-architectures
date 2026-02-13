from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from saga_choreography.models.tables import User


async def get_user_by_id(user_id: int, db: AsyncSession) -> User | None:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_user_profile(user_id: int, db: AsyncSession) -> dict | None:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        return None
    return {
        "id": user.id,
        "username": user.username,
        "full_name": user.full_name,
        "bio": user.bio,
        "profile_image_url": user.profile_image_url,
        "post_count": user.post_count,
        "follower_count": user.follower_count,
        "following_count": user.following_count,
    }


async def update_user(
    user_id: int,
    full_name: str | None,
    bio: str | None,
    profile_image_url: str | None,
    db: AsyncSession,
) -> User:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if full_name is not None:
        user.full_name = full_name
    if bio is not None:
        user.bio = bio
    if profile_image_url is not None:
        user.profile_image_url = profile_image_url
    await db.flush()
    return user
