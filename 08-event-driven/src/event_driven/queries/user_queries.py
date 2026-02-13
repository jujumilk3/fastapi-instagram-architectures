from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from event_driven.models.tables import User


async def get_user_by_id(user_id: int, db: AsyncSession) -> User | None:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_user_by_email(email: str, db: AsyncSession) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
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
