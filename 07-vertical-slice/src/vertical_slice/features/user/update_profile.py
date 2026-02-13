from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from vertical_slice.models.tables import User


@dataclass
class UpdateProfileRequest:
    user_id: int
    data: dict
    db: AsyncSession


@dataclass
class UpdateProfileResponse:
    id: int
    username: str
    email: str
    full_name: str | None
    bio: str | None
    profile_image_url: str | None
    is_active: bool
    created_at: datetime


async def update_profile_handler(request: UpdateProfileRequest) -> UpdateProfileResponse:
    db = request.db
    user = await db.get(User, request.user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    for key, value in request.data.items():
        setattr(user, key, value)
    await db.flush()
    await db.refresh(user)

    return UpdateProfileResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        bio=user.bio,
        profile_image_url=user.profile_image_url,
        is_active=user.is_active,
        created_at=user.created_at,
    )
