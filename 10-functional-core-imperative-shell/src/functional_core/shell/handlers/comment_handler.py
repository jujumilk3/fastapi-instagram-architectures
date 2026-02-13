from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from functional_core.core.comment import can_delete_comment
from functional_core.core.notification import create_notification_data
from functional_core.shell.models import Comment, Notification, Post


async def create_comment(
    db: AsyncSession, post_id: int, author_id: int, content: str
) -> Comment:
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    comment = Comment(post_id=post_id, author_id=author_id, content=content)
    db.add(comment)
    await db.flush()
    await db.refresh(comment)

    if post.author_id != author_id:
        notif_data = create_notification_data("comment", author_id, post.author_id, post_id)
        db.add(Notification(**notif_data))
        await db.flush()

    return comment


async def get_comments_by_post(
    db: AsyncSession, post_id: int, limit: int = 50, offset: int = 0
) -> list[Comment]:
    result = await db.execute(
        select(Comment)
        .options(selectinload(Comment.author))
        .where(Comment.post_id == post_id)
        .order_by(Comment.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return list(result.scalars().all())


async def delete_comment(db: AsyncSession, comment_id: int, user_id: int) -> None:
    comment = await db.get(Comment, comment_id)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")

    if not can_delete_comment(comment.author_id, user_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your comment")

    await db.delete(comment)
    await db.flush()
