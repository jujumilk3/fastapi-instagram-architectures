from sqlalchemy import select
from sqlalchemy.orm import selectinload

from actor_model.actors.base import Actor, Message
from actor_model.actors.messages import GetFeedMessage
from actor_model.models.tables import Follow, Post


class FeedActor(Actor):
    async def receive(self, message: Message):
        match message:
            case GetFeedMessage():
                await self._handle_get_feed(message)

    async def _handle_get_feed(self, msg: GetFeedMessage):
        async with msg.db_factory() as db:
            following_result = await db.execute(
                select(Follow.following_id).where(Follow.follower_id == msg.user_id)
            )
            following_ids = list(following_result.scalars().all())
            following_ids.append(msg.user_id)

            result = await db.execute(
                select(Post)
                .options(selectinload(Post.author), selectinload(Post.likes), selectinload(Post.comments))
                .where(Post.author_id.in_(following_ids))
                .order_by(Post.created_at.desc())
                .limit(msg.limit)
                .offset(msg.offset)
            )

            posts = [
                {
                    "id": p.id,
                    "author_id": p.author_id,
                    "author_username": p.author.username if p.author else None,
                    "content": p.content,
                    "image_url": p.image_url,
                    "like_count": len(p.likes) if p.likes else 0,
                    "comment_count": len(p.comments) if p.comments else 0,
                    "created_at": p.created_at,
                }
                for p in result.scalars().all()
            ]
            msg.reply(posts)
