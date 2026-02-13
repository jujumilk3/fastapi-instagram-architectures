from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from vertical_slice.models.tables import Follow, User


@dataclass
class GetFollowingRequest:
    user_id: int
    db: AsyncSession


@dataclass
class UserItem:
    id: int
    username: str
    email: str
    full_name: str | None
    bio: str | None
    profile_image_url: str | None
    is_active: bool
    created_at: datetime


async def get_following_handler(request: GetFollowingRequest) -> list[UserItem]:
    db = request.db
    result = await db.execute(
        select(User).join(Follow, Follow.following_id == User.id).where(Follow.follower_id == request.user_id)
    )
    return [
        UserItem(
            id=u.id, username=u.username, email=u.email,
            full_name=u.full_name, bio=u.bio,
            profile_image_url=u.profile_image_url,
            is_active=u.is_active, created_at=u.created_at,
        )
        for u in result.scalars().all()
    ]
