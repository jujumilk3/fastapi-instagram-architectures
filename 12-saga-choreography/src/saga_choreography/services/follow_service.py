from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from saga_choreography.models.tables import Follow, User


async def create_follow(follower_id: int, following_id: int, db: AsyncSession) -> Follow:
    if follower_id == following_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot follow yourself")

    existing = await db.execute(
        select(Follow).where(Follow.follower_id == follower_id, Follow.following_id == following_id)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Already following")

    follow = Follow(follower_id=follower_id, following_id=following_id)
    db.add(follow)

    follower_result = await db.execute(select(User).where(User.id == follower_id))
    follower = follower_result.scalar_one_or_none()
    following_result = await db.execute(select(User).where(User.id == following_id))
    following = following_result.scalar_one_or_none()

    if follower:
        follower.following_count += 1
    if following:
        following.follower_count += 1

    await db.flush()
    return follow


async def delete_follow(follower_id: int, following_id: int, db: AsyncSession) -> None:
    result = await db.execute(
        select(Follow).where(Follow.follower_id == follower_id, Follow.following_id == following_id)
    )
    follow = result.scalar_one_or_none()
    if not follow:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not following")

    follower_result = await db.execute(select(User).where(User.id == follower_id))
    follower = follower_result.scalar_one_or_none()
    following_result = await db.execute(select(User).where(User.id == following_id))
    following = following_result.scalar_one_or_none()

    if follower and follower.following_count > 0:
        follower.following_count -= 1
    if following and following.follower_count > 0:
        following.follower_count -= 1

    await db.delete(follow)
    await db.flush()
