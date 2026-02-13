from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from vertical_slice.models.tables import User
from vertical_slice.shared.security import hash_password


@dataclass
class RegisterRequest:
    username: str
    email: str
    password: str
    full_name: str | None
    db: AsyncSession


@dataclass
class RegisterResponse:
    id: int
    username: str
    email: str
    full_name: str | None
    bio: str | None
    profile_image_url: str | None
    is_active: bool
    created_at: datetime


async def register_handler(request: RegisterRequest) -> RegisterResponse:
    db = request.db

    existing = await db.execute(select(User).where(User.email == request.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    existing = await db.execute(select(User).where(User.username == request.username))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken")

    user = User(
        username=request.username,
        email=request.email,
        hashed_password=hash_password(request.password),
        full_name=request.full_name,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)

    return RegisterResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        bio=user.bio,
        profile_image_url=user.profile_image_url,
        is_active=user.is_active,
        created_at=user.created_at,
    )
