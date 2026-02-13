from sqlalchemy import select
from sqlalchemy.orm import selectinload

from actor_model.actors.base import Actor, Message
from actor_model.actors.messages import (
    GetPostsByHashtagMessage,
    SearchHashtagsMessage,
    SearchUsersMessage,
)
from actor_model.models.tables import Hashtag, Post, PostHashtag, User


class SearchActor(Actor):
    async def receive(self, message: Message):
        match message:
            case SearchUsersMessage():
                await self._handle_search_users(message)
            case SearchHashtagsMessage():
                await self._handle_search_hashtags(message)
            case GetPostsByHashtagMessage():
                await self._handle_posts_by_hashtag(message)

    async def _handle_search_users(self, msg: SearchUsersMessage):
        async with msg.db_factory() as db:
            result = await db.execute(
                select(User).where(User.username.ilike(f"%{msg.query}%")).limit(msg.limit)
            )
            users = [
                {
                    "id": u.id,
                    "username": u.username,
                    "email": u.email,
                    "full_name": u.full_name,
                    "bio": u.bio,
                    "profile_image_url": u.profile_image_url,
                    "is_active": u.is_active,
                    "created_at": u.created_at,
                }
                for u in result.scalars().all()
            ]
            msg.reply(users)

    async def _handle_search_hashtags(self, msg: SearchHashtagsMessage):
        async with msg.db_factory() as db:
            result = await db.execute(
                select(Hashtag).where(Hashtag.name.ilike(f"%{msg.query}%")).limit(msg.limit)
            )
            hashtags = [
                {"id": h.id, "name": h.name}
                for h in result.scalars().all()
            ]
            msg.reply(hashtags)

    async def _handle_posts_by_hashtag(self, msg: GetPostsByHashtagMessage):
        async with msg.db_factory() as db:
            result = await db.execute(
                select(Post)
                .join(PostHashtag, Post.id == PostHashtag.post_id)
                .join(Hashtag, PostHashtag.hashtag_id == Hashtag.id)
                .options(selectinload(Post.author), selectinload(Post.likes), selectinload(Post.comments))
                .where(Hashtag.name == msg.tag)
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
