from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from functional_core.core.auth import create_token_payload, validate_credentials, validate_registration
from functional_core.shell.models import User
from functional_core.shell.security import create_access_token, hash_password, verify_password


async def register_user(
    db: AsyncSession,
    username: str,
    email: str,
    password: str,
    full_name: str | None = None,
) -> User:
    existing_email = await db.execute(select(User.email).where(User.email == email))
    existing_username = await db.execute(select(User.username).where(User.username == username))

    existing_emails = [row[0] for row in existing_email.all()]
    existing_usernames = [row[0] for row in existing_username.all()]

    result = validate_registration(username, email, existing_emails, existing_usernames)
    if not result.success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result.error)

    hashed = hash_password(password)
    user = User(
        username=username,
        email=email,
        hashed_password=hashed,
        full_name=full_name,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


async def login_user(db: AsyncSession, email: str, password: str) -> dict:
    row = await db.execute(select(User).where(User.email == email))
    user = row.scalar_one_or_none()

    password_matches = verify_password(password, user.hashed_password) if user else False
    result = validate_credentials(
        user.hashed_password if user else None,
        password_matches,
    )
    if not result.success:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=result.error)

    payload = create_token_payload(user.id)
    token = create_access_token(payload)
    return {"access_token": token, "token_type": "bearer"}


async def get_current_user(db: AsyncSession, user_id: int) -> User:
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user
