from fastapi import HTTPException, status
from sqlalchemy import select

from cqrs_es.read.projections.models import UserProjection
from cqrs_es.shared import event_bus, security
from cqrs_es.shared.event_store import append_event, get_next_version
from cqrs_es.write.aggregates.user import UserAggregate
from cqrs_es.write.commands.commands import LoginUser, RegisterUser, UpdateUser


async def handle_register_user(cmd: RegisterUser) -> dict:
    existing = await cmd.db.execute(
        select(UserProjection).where(UserProjection.email == cmd.email)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    existing_username = await cmd.db.execute(
        select(UserProjection).where(UserProjection.username == cmd.username)
    )
    if existing_username.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken")

    # ID generation: get max ID from projection + 1
    result = await cmd.db.execute(
        select(UserProjection.id).order_by(UserProjection.id.desc()).limit(1)
    )
    max_id = result.scalar_one_or_none() or 0
    user_id = max_id + 1

    hashed_pw = security.hash_password(cmd.password)
    event_type, event_data = UserAggregate.register(
        user_id, cmd.username, cmd.email, hashed_pw, cmd.full_name
    )

    version = await get_next_version(cmd.db, "User", str(user_id))
    await append_event(cmd.db, "User", str(user_id), event_type, event_data, version)
    await event_bus.publish(event_type, event_data, db=cmd.db)

    return {
        "id": user_id,
        "username": cmd.username,
        "email": cmd.email,
        "full_name": cmd.full_name,
        "bio": None,
        "profile_image_url": None,
        "is_active": True,
        "created_at": event_data["created_at"],
    }


async def handle_login_user(cmd: LoginUser) -> str:
    result = await cmd.db.execute(
        select(UserProjection).where(UserProjection.email == cmd.email)
    )
    user = result.scalar_one_or_none()
    if not user or not security.verify_password(cmd.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return security.create_token({"sub": str(user.id)})


async def handle_update_user(cmd: UpdateUser) -> dict:
    result = await cmd.db.execute(
        select(UserProjection).where(UserProjection.id == cmd.user_id)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    updates = {}
    if cmd.full_name is not None:
        updates["full_name"] = cmd.full_name
    if cmd.bio is not None:
        updates["bio"] = cmd.bio
    if cmd.profile_image_url is not None:
        updates["profile_image_url"] = cmd.profile_image_url

    if not updates:
        return {
            "id": user.id, "username": user.username, "email": user.email,
            "full_name": user.full_name, "bio": user.bio,
            "profile_image_url": user.profile_image_url,
            "is_active": user.is_active, "created_at": user.created_at,
        }

    event_type, event_data = UserAggregate.update(cmd.user_id, **updates)
    version = await get_next_version(cmd.db, "User", str(cmd.user_id))
    await append_event(cmd.db, "User", str(cmd.user_id), event_type, event_data, version)
    await event_bus.publish(event_type, event_data, db=cmd.db)

    # Re-read updated projection
    result = await cmd.db.execute(
        select(UserProjection).where(UserProjection.id == cmd.user_id)
    )
    user = result.scalar_one()
    return {
        "id": user.id, "username": user.username, "email": user.email,
        "full_name": user.full_name, "bio": user.bio,
        "profile_image_url": user.profile_image_url,
        "is_active": user.is_active, "created_at": user.created_at,
    }
