from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from event_driven.events.definitions import POST_CREATED, POST_DELETED
from event_driven.models.tables import Post, User
from event_driven.shared.event_broker import broker


async def create_post(
    author_id: int,
    content: str | None,
    image_url: str | None,
    db: AsyncSession,
) -> dict:
    user_result = await db.execute(select(User).where(User.id == author_id))
    user = user_result.scalar_one_or_none()

    post = Post(author_id=author_id, content=content, image_url=image_url)
    db.add(post)

    if user:
        user.post_count += 1

    await db.flush()

    await broker.publish(POST_CREATED, {
        "post_id": post.id,
        "author_id": author_id,
        "content": content,
        "db": db,
    })

    return {
        "id": post.id,
        "author_id": post.author_id,
        "author_username": user.username if user else None,
        "content": post.content,
        "image_url": post.image_url,
        "like_count": post.like_count,
        "comment_count": post.comment_count,
        "created_at": post.created_at,
    }


async def delete_post(post_id: int, user_id: int, db: AsyncSession) -> None:
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    if post.author_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your post")

    user_result = await db.execute(select(User).where(User.id == user_id))
    user = user_result.scalar_one_or_none()
    if user and user.post_count > 0:
        user.post_count -= 1

    await db.delete(post)
    await db.flush()

    await broker.publish(POST_DELETED, {"post_id": post_id, "author_id": user_id, "db": db})
