from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from event_driven.events.definitions import COMMENT_ADDED, COMMENT_DELETED
from event_driven.models.tables import Comment, Post, User
from event_driven.shared.event_broker import broker


async def create_comment(
    post_id: int,
    author_id: int,
    content: str,
    db: AsyncSession,
) -> dict:
    post_result = await db.execute(select(Post).where(Post.id == post_id))
    post = post_result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    user_result = await db.execute(select(User).where(User.id == author_id))
    user = user_result.scalar_one_or_none()

    comment = Comment(post_id=post_id, author_id=author_id, content=content)
    db.add(comment)
    post.comment_count += 1
    await db.flush()

    await broker.publish(COMMENT_ADDED, {
        "comment_id": comment.id,
        "post_id": post_id,
        "post_author_id": post.author_id,
        "author_id": author_id,
        "db": db,
    })

    return {
        "id": comment.id,
        "post_id": comment.post_id,
        "author_id": comment.author_id,
        "author_username": user.username if user else None,
        "content": comment.content,
        "created_at": comment.created_at,
    }


async def delete_comment(comment_id: int, user_id: int, db: AsyncSession) -> None:
    result = await db.execute(select(Comment).where(Comment.id == comment_id))
    comment = result.scalar_one_or_none()
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    if comment.author_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your comment")

    post_result = await db.execute(select(Post).where(Post.id == comment.post_id))
    post = post_result.scalar_one_or_none()
    if post and post.comment_count > 0:
        post.comment_count -= 1

    post_id = comment.post_id
    await db.delete(comment)
    await db.flush()

    await broker.publish(COMMENT_DELETED, {
        "comment_id": comment_id,
        "post_id": post_id,
        "db": db,
    })
