from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from actor_model.actors.base import Actor, Message
from actor_model.actors.messages import (
    CreateCommentMessage,
    DeleteCommentMessage,
    GetCommentsMessage,
)
from actor_model.actors.registry import ActorRegistry
from actor_model.models.tables import Comment, Notification, Post


class CommentActor(Actor):
    def __init__(self, registry: ActorRegistry):
        super().__init__()
        self._registry = registry

    async def receive(self, message: Message):
        match message:
            case CreateCommentMessage():
                await self._handle_create(message)
            case GetCommentsMessage():
                await self._handle_get(message)
            case DeleteCommentMessage():
                await self._handle_delete(message)

    async def _handle_create(self, msg: CreateCommentMessage):
        async with msg.db_factory() as db:
            post_result = await db.execute(select(Post).where(Post.id == msg.post_id))
            post = post_result.scalar_one_or_none()
            if not post:
                raise ValueError("Post not found")

            comment = Comment(post_id=msg.post_id, author_id=msg.author_id, content=msg.content)
            db.add(comment)
            await db.flush()
            await db.refresh(comment)

            if post.author_id != msg.author_id:
                db.add(Notification(
                    user_id=post.author_id,
                    actor_id=msg.author_id,
                    type="comment",
                    reference_id=msg.post_id,
                    message=f"User {msg.author_id} commented on your post",
                ))
                await db.flush()

            result = {
                "id": comment.id,
                "post_id": comment.post_id,
                "author_id": comment.author_id,
                "content": comment.content,
                "created_at": comment.created_at,
            }
            await db.commit()
            msg.reply(result)

    async def _handle_get(self, msg: GetCommentsMessage):
        async with msg.db_factory() as db:
            result = await db.execute(
                select(Comment)
                .options(selectinload(Comment.author))
                .where(Comment.post_id == msg.post_id)
                .order_by(Comment.created_at.desc())
                .limit(msg.limit)
                .offset(msg.offset)
            )
            comments = [
                {
                    "id": c.id,
                    "post_id": c.post_id,
                    "author_id": c.author_id,
                    "author_username": c.author.username if c.author else None,
                    "content": c.content,
                    "created_at": c.created_at,
                }
                for c in result.scalars().all()
            ]
            msg.reply(comments)

    async def _handle_delete(self, msg: DeleteCommentMessage):
        async with msg.db_factory() as db:
            comment = await db.get(Comment, msg.comment_id)
            if not comment:
                raise ValueError("Comment not found")
            if comment.author_id != msg.user_id:
                raise PermissionError("Not your comment")

            await db.delete(comment)
            await db.commit()
            msg.reply(None)
