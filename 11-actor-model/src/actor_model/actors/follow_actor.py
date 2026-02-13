from sqlalchemy import select

from actor_model.actors.base import Actor, Message
from actor_model.actors.messages import FollowUserMessage, UnfollowUserMessage
from actor_model.actors.registry import ActorRegistry
from actor_model.models.tables import Follow, Notification, User


class FollowActor(Actor):
    def __init__(self, registry: ActorRegistry):
        super().__init__()
        self._registry = registry

    async def receive(self, message: Message):
        match message:
            case FollowUserMessage():
                await self._handle_follow(message)
            case UnfollowUserMessage():
                await self._handle_unfollow(message)

    async def _handle_follow(self, msg: FollowUserMessage):
        async with msg.db_factory() as db:
            if msg.follower_id == msg.following_id:
                raise ValueError("Cannot follow yourself")

            target = await db.get(User, msg.following_id)
            if not target:
                raise ValueError("User not found")

            existing_result = await db.execute(
                select(Follow).where(
                    Follow.follower_id == msg.follower_id, Follow.following_id == msg.following_id
                )
            )
            if existing_result.scalar_one_or_none():
                raise ValueError("Already following")

            db.add(Follow(follower_id=msg.follower_id, following_id=msg.following_id))
            db.add(Notification(
                user_id=msg.following_id,
                actor_id=msg.follower_id,
                type="follow",
                message=f"User {msg.follower_id} started following you",
            ))
            await db.commit()
            msg.reply({"following": True})

    async def _handle_unfollow(self, msg: UnfollowUserMessage):
        async with msg.db_factory() as db:
            existing_result = await db.execute(
                select(Follow).where(
                    Follow.follower_id == msg.follower_id, Follow.following_id == msg.following_id
                )
            )
            existing = existing_result.scalar_one_or_none()
            if not existing:
                raise ValueError("Not following")

            await db.delete(existing)
            await db.commit()
            msg.reply({"following": False})
