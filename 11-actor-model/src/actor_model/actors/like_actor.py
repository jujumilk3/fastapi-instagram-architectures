from sqlalchemy import func, select

from actor_model.actors.base import Actor, Message
from actor_model.actors.messages import ToggleLikeMessage
from actor_model.actors.registry import ActorRegistry
from actor_model.models.tables import Like, Notification, Post


class LikeActor(Actor):
    def __init__(self, registry: ActorRegistry):
        super().__init__()
        self._registry = registry

    async def receive(self, message: Message):
        match message:
            case ToggleLikeMessage():
                await self._handle_toggle(message)

    async def _handle_toggle(self, msg: ToggleLikeMessage):
        async with msg.db_factory() as db:
            post_result = await db.execute(select(Post).where(Post.id == msg.post_id))
            post = post_result.scalar_one_or_none()
            if not post:
                raise ValueError("Post not found")

            existing_result = await db.execute(
                select(Like).where(Like.post_id == msg.post_id, Like.user_id == msg.user_id)
            )
            existing = existing_result.scalar_one_or_none()

            if existing:
                await db.delete(existing)
                liked = False
            else:
                db.add(Like(post_id=msg.post_id, user_id=msg.user_id))
                liked = True

                if post.author_id != msg.user_id:
                    db.add(Notification(
                        user_id=post.author_id,
                        actor_id=msg.user_id,
                        type="like",
                        reference_id=msg.post_id,
                        message=f"User {msg.user_id} liked your post",
                    ))

            await db.flush()

            count_result = await db.execute(
                select(func.count()).select_from(Like).where(Like.post_id == msg.post_id)
            )
            await db.commit()
            msg.reply({"liked": liked, "like_count": count_result.scalar_one()})
