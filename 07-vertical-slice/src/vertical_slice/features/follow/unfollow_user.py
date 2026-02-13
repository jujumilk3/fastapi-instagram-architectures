from __future__ import annotations

from dataclasses import dataclass

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from vertical_slice.models.tables import Follow


@dataclass
class UnfollowUserRequest:
    follower_id: int
    following_id: int
    db: AsyncSession


@dataclass
class UnfollowUserResponse:
    following: bool


async def unfollow_user_handler(request: UnfollowUserRequest) -> UnfollowUserResponse:
    db = request.db
    result = await db.execute(
        select(Follow).where(Follow.follower_id == request.follower_id, Follow.following_id == request.following_id)
    )
    existing = result.scalar_one_or_none()
    if not existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not following")
    await db.delete(existing)
    await db.flush()
    return UnfollowUserResponse(following=False)
