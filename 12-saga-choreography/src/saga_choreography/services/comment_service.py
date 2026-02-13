from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from saga_choreography.models.tables import Comment, Post, User


async def create_comment(
    post_id: int,
    author_id: int,
    content: str,
    db: AsyncSession,
) -> Comment:
    post_result = await db.execute(select(Post).where(Post.id == post_id))
    post = post_result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    comment = Comment(post_id=post_id, author_id=author_id, content=content)
    db.add(comment)
    post.comment_count += 1
    await db.flush()
    return comment


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

    await db.delete(comment)
    await db.flush()


async def delete_comment_by_id(comment_id: int, db: AsyncSession) -> None:
    result = await db.execute(select(Comment).where(Comment.id == comment_id))
    comment = result.scalar_one_or_none()
    if comment:
        post_result = await db.execute(select(Post).where(Post.id == comment.post_id))
        post = post_result.scalar_one_or_none()
        if post and post.comment_count > 0:
            post.comment_count -= 1
        await db.delete(comment)
        await db.flush()
