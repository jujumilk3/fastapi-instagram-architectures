from __future__ import annotations

from dataclasses import dataclass

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from vertical_slice.models.tables import User
from vertical_slice.shared.security import create_access_token, verify_password


@dataclass
class LoginRequest:
    email: str
    password: str
    db: AsyncSession


@dataclass
class LoginResponse:
    access_token: str
    token_type: str = "bearer"


async def login_handler(request: LoginRequest) -> LoginResponse:
    db = request.db

    result = await db.execute(select(User).where(User.email == request.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_access_token({"sub": str(user.id)})
    return LoginResponse(access_token=token)
