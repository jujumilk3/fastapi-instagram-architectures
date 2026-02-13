from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from functional_core.shell.models import Follow, Post, User


async def get_profile(db: AsyncSession, user_id: int) -> dict:
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    post_count_result = await db.execute(
        select(func.count()).select_from(Post).where(Post.author_id == user_id)
    )
    follower_count_result = await db.execute(
        select(func.count()).select_from(Follow).where(Follow.following_id == user_id)
    )
    following_count_result = await db.execute(
        select(func.count()).select_from(Follow).where(Follow.follower_id == user_id)
    )

    return {
        "id": user.id,
        "username": user.username,
        "full_name": user.full_name,
        "bio": user.bio,
        "profile_image_url": user.profile_image_url,
        "post_count": post_count_result.scalar_one(),
        "follower_count": follower_count_result.scalar_one(),
        "following_count": following_count_result.scalar_one(),
    }


async def update_profile(db: AsyncSession, user_id: int, update_data: dict) -> User:
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    for key, value in update_data.items():
        setattr(user, key, value)

    await db.flush()
    await db.refresh(user)
    return user


async def get_followers(db: AsyncSession, user_id: int) -> list[User]:
    result = await db.execute(
        select(Follow.follower_id).where(Follow.following_id == user_id)
    )
    follower_ids = list(result.scalars().all())
    users = []
    for fid in follower_ids:
        user = await db.get(User, fid)
        if user:
            users.append(user)
    return users


async def get_following(db: AsyncSession, user_id: int) -> list[User]:
    result = await db.execute(
        select(Follow.following_id).where(Follow.follower_id == user_id)
    )
    following_ids = list(result.scalars().all())
    users = []
    for fid in following_ids:
        user = await db.get(User, fid)
        if user:
            users.append(user)
    return users
