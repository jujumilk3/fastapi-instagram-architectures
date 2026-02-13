from __future__ import annotations

from dataclasses import dataclass

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from vertical_slice.models.tables import Follow, Notification, User


@dataclass
class FollowUserRequest:
    follower_id: int
    following_id: int
    db: AsyncSession


@dataclass
class FollowUserResponse:
    following: bool


async def follow_user_handler(request: FollowUserRequest) -> FollowUserResponse:
    db = request.db

    if request.follower_id == request.following_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot follow yourself")

    target = await db.get(User, request.following_id)
    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    result = await db.execute(
        select(Follow).where(Follow.follower_id == request.follower_id, Follow.following_id == request.following_id)
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Already following")

    db.add(Follow(follower_id=request.follower_id, following_id=request.following_id))
    db.add(Notification(
        user_id=request.following_id,
        actor_id=request.follower_id,
        type="follow",
        message="started following you",
    ))
    await db.flush()

    return FollowUserResponse(following=True)
