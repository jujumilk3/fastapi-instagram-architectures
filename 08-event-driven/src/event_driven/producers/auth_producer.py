from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from event_driven.events.definitions import USER_REGISTERED, USER_UPDATED
from event_driven.models.tables import User
from event_driven.shared.event_broker import broker
from event_driven.shared.security import create_token, hash_password, verify_password


async def register_user(
    username: str,
    email: str,
    password: str,
    full_name: str | None,
    db: AsyncSession,
) -> User:
    existing = await db.execute(select(User).where(User.email == email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    existing_username = await db.execute(select(User).where(User.username == username))
    if existing_username.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken")

    user = User(
        username=username,
        email=email,
        hashed_password=hash_password(password),
        full_name=full_name,
    )
    db.add(user)
    await db.flush()

    await broker.publish(USER_REGISTERED, {"user_id": user.id, "username": username, "db": db})

    return user


async def login_user(email: str, password: str, db: AsyncSession) -> str:
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return create_token({"sub": str(user.id)})


async def update_user(
    user_id: int,
    full_name: str | None,
    bio: str | None,
    profile_image_url: str | None,
    db: AsyncSession,
) -> User:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if full_name is not None:
        user.full_name = full_name
    if bio is not None:
        user.bio = bio
    if profile_image_url is not None:
        user.profile_image_url = profile_image_url
    await db.flush()

    await broker.publish(USER_UPDATED, {"user_id": user.id, "db": db})

    return user
