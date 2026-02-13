import re

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from actor_model.actors.base import Actor, Message
from actor_model.actors.messages import (
    CreatePostMessage,
    DeletePostMessage,
    GetPostMessage,
    GetUserPostsMessage,
)
from actor_model.models.tables import Hashtag, Post, PostHashtag


def _extract_hashtags(content: str | None) -> list[str]:
    if not content:
        return []
    return re.findall(r"#(\w+)", content)


async def _get_post_with_relations(db: AsyncSession, post_id: int) -> Post | None:
    result = await db.execute(
        select(Post)
        .options(selectinload(Post.author), selectinload(Post.likes), selectinload(Post.comments))
        .where(Post.id == post_id)
    )
    return result.scalar_one_or_none()


def _post_to_dict(post: Post) -> dict:
    return {
        "id": post.id,
        "author_id": post.author_id,
        "author_username": post.author.username if post.author else None,
        "content": post.content,
        "image_url": post.image_url,
        "like_count": len(post.likes) if post.likes else 0,
        "comment_count": len(post.comments) if post.comments else 0,
        "created_at": post.created_at,
    }


class PostActor(Actor):
    async def receive(self, message: Message):
        match message:
            case CreatePostMessage():
                await self._handle_create(message)
            case GetPostMessage():
                await self._handle_get(message)
            case DeletePostMessage():
                await self._handle_delete(message)
            case GetUserPostsMessage():
                await self._handle_get_user_posts(message)

    async def _handle_create(self, msg: CreatePostMessage):
        async with msg.db_factory() as db:
            post = Post(author_id=msg.author_id, content=msg.content, image_url=msg.image_url)
            db.add(post)
            await db.flush()

            tags = _extract_hashtags(msg.content)
            for tag_name in tags:
                tag_lower = tag_name.lower()
                result = await db.execute(select(Hashtag).where(Hashtag.name == tag_lower))
                hashtag = result.scalar_one_or_none()
                if not hashtag:
                    hashtag = Hashtag(name=tag_lower)
                    db.add(hashtag)
                    await db.flush()
                    await db.refresh(hashtag)

                existing_link = await db.execute(
                    select(PostHashtag).where(
                        PostHashtag.post_id == post.id, PostHashtag.hashtag_id == hashtag.id
                    )
                )
                if not existing_link.scalar_one_or_none():
                    db.add(PostHashtag(post_id=post.id, hashtag_id=hashtag.id))
                    await db.flush()

            loaded_post = await _get_post_with_relations(db, post.id)
            result = _post_to_dict(loaded_post)
            await db.commit()
            msg.reply(result)

    async def _handle_get(self, msg: GetPostMessage):
        async with msg.db_factory() as db:
            post = await _get_post_with_relations(db, msg.post_id)
            if not post:
                raise ValueError("Post not found")
            msg.reply(_post_to_dict(post))

    async def _handle_delete(self, msg: DeletePostMessage):
        async with msg.db_factory() as db:
            post = await _get_post_with_relations(db, msg.post_id)
            if not post:
                raise ValueError("Post not found")
            if post.author_id != msg.user_id:
                raise PermissionError("Not your post")

            link_result = await db.execute(select(PostHashtag).where(PostHashtag.post_id == msg.post_id))
            for ph in link_result.scalars().all():
                await db.delete(ph)
            await db.flush()

            await db.delete(post)
            await db.commit()
            msg.reply(None)

    async def _handle_get_user_posts(self, msg: GetUserPostsMessage):
        async with msg.db_factory() as db:
            result = await db.execute(
                select(Post)
                .options(selectinload(Post.author), selectinload(Post.likes), selectinload(Post.comments))
                .where(Post.author_id == msg.user_id)
                .order_by(Post.created_at.desc())
                .limit(msg.limit)
                .offset(msg.offset)
            )
            posts = [_post_to_dict(p) for p in result.scalars().all()]
            msg.reply(posts)
