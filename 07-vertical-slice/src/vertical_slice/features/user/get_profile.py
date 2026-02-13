from __future__ import annotations

from dataclasses import dataclass

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from vertical_slice.models.tables import Follow, Post, User


@dataclass
class GetProfileRequest:
    user_id: int
    db: AsyncSession


@dataclass
class GetProfileResponse:
    id: int
    username: str
    full_name: str | None
    bio: str | None
    profile_image_url: str | None
    post_count: int
    follower_count: int
    following_count: int


async def get_profile_handler(request: GetProfileRequest) -> GetProfileResponse:
    db = request.db
    user = await db.get(User, request.user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    post_count = (await db.execute(
        select(func.count()).select_from(Post).where(Post.author_id == request.user_id)
    )).scalar_one()
    follower_count = (await db.execute(
        select(func.count()).select_from(Follow).where(Follow.following_id == request.user_id)
    )).scalar_one()
    following_count = (await db.execute(
        select(func.count()).select_from(Follow).where(Follow.follower_id == request.user_id)
    )).scalar_one()

    return GetProfileResponse(
        id=user.id,
        username=user.username,
        full_name=user.full_name,
        bio=user.bio,
        profile_image_url=user.profile_image_url,
        post_count=post_count,
        follower_count=follower_count,
        following_count=following_count,
    )
