from sqlalchemy import func, select

from actor_model.actors.base import Actor, Message
from actor_model.actors.messages import (
    GetCurrentUserMessage,
    GetFollowersMessage,
    GetFollowingMessage,
    GetProfileMessage,
    LoginMessage,
    RegisterMessage,
    UpdateProfileMessage,
)
from actor_model.models.tables import Follow, Post, User
from actor_model.shared.security import (
    create_access_token,
    hash_password,
    verify_password,
)


class UserActor(Actor):
    async def receive(self, message: Message):
        match message:
            case RegisterMessage():
                await self._handle_register(message)
            case LoginMessage():
                await self._handle_login(message)
            case GetCurrentUserMessage():
                await self._handle_get_current_user(message)
            case GetProfileMessage():
                await self._handle_get_profile(message)
            case UpdateProfileMessage():
                await self._handle_update_profile(message)
            case GetFollowersMessage():
                await self._handle_get_followers(message)
            case GetFollowingMessage():
                await self._handle_get_following(message)

    async def _handle_register(self, msg: RegisterMessage):
        async with msg.db_factory() as db:
            existing_email = await db.execute(select(User.email).where(User.email == msg.email))
            if existing_email.scalar_one_or_none():
                raise ValueError("Email already registered")

            existing_username = await db.execute(select(User.username).where(User.username == msg.username))
            if existing_username.scalar_one_or_none():
                raise ValueError("Username already taken")

            hashed = hash_password(msg.password)
            user = User(
                username=msg.username,
                email=msg.email,
                hashed_password=hashed,
                full_name=msg.full_name,
            )
            db.add(user)
            await db.flush()
            await db.refresh(user)

            result = {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "bio": user.bio,
                "profile_image_url": user.profile_image_url,
                "is_active": user.is_active,
                "created_at": user.created_at,
            }
            await db.commit()
            msg.reply(result)

    async def _handle_login(self, msg: LoginMessage):
        async with msg.db_factory() as db:
            row = await db.execute(select(User).where(User.email == msg.email))
            user = row.scalar_one_or_none()

            if not user or not verify_password(msg.password, user.hashed_password):
                raise ValueError("Invalid credentials")

            token = create_access_token({"sub": str(user.id)})
            msg.reply({"access_token": token, "token_type": "bearer"})

    async def _handle_get_current_user(self, msg: GetCurrentUserMessage):
        async with msg.db_factory() as db:
            user = await db.get(User, msg.user_id)
            if not user:
                raise ValueError("User not found")

            msg.reply({
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "bio": user.bio,
                "profile_image_url": user.profile_image_url,
                "is_active": user.is_active,
                "created_at": user.created_at,
            })

    async def _handle_get_profile(self, msg: GetProfileMessage):
        async with msg.db_factory() as db:
            user = await db.get(User, msg.user_id)
            if not user:
                raise ValueError("User not found")

            post_count = (await db.execute(
                select(func.count()).select_from(Post).where(Post.author_id == msg.user_id)
            )).scalar_one()
            follower_count = (await db.execute(
                select(func.count()).select_from(Follow).where(Follow.following_id == msg.user_id)
            )).scalar_one()
            following_count = (await db.execute(
                select(func.count()).select_from(Follow).where(Follow.follower_id == msg.user_id)
            )).scalar_one()

            msg.reply({
                "id": user.id,
                "username": user.username,
                "full_name": user.full_name,
                "bio": user.bio,
                "profile_image_url": user.profile_image_url,
                "post_count": post_count,
                "follower_count": follower_count,
                "following_count": following_count,
            })

    async def _handle_update_profile(self, msg: UpdateProfileMessage):
        async with msg.db_factory() as db:
            user = await db.get(User, msg.user_id)
            if not user:
                raise ValueError("User not found")

            for key, value in msg.update_data.items():
                setattr(user, key, value)

            await db.flush()
            await db.refresh(user)

            result = {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "bio": user.bio,
                "profile_image_url": user.profile_image_url,
                "is_active": user.is_active,
                "created_at": user.created_at,
            }
            await db.commit()
            msg.reply(result)

    async def _handle_get_followers(self, msg: GetFollowersMessage):
        async with msg.db_factory() as db:
            result = await db.execute(
                select(Follow.follower_id).where(Follow.following_id == msg.user_id)
            )
            follower_ids = list(result.scalars().all())
            users = []
            for fid in follower_ids:
                user = await db.get(User, fid)
                if user:
                    users.append({
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                        "full_name": user.full_name,
                        "bio": user.bio,
                        "profile_image_url": user.profile_image_url,
                        "is_active": user.is_active,
                        "created_at": user.created_at,
                    })
            msg.reply(users)

    async def _handle_get_following(self, msg: GetFollowingMessage):
        async with msg.db_factory() as db:
            result = await db.execute(
                select(Follow.following_id).where(Follow.follower_id == msg.user_id)
            )
            following_ids = list(result.scalars().all())
            users = []
            for fid in following_ids:
                user = await db.get(User, fid)
                if user:
                    users.append({
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                        "full_name": user.full_name,
                        "bio": user.bio,
                        "profile_image_url": user.profile_image_url,
                        "is_active": user.is_active,
                        "created_at": user.created_at,
                    })
            msg.reply(users)
