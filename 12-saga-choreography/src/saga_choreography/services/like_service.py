from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from saga_choreography.models.tables import Like, Post


async def add_like(post_id: int, user_id: int, db: AsyncSession) -> Like:
    post_result = await db.execute(select(Post).where(Post.id == post_id))
    post = post_result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    existing = await db.execute(
        select(Like).where(Like.post_id == post_id, Like.user_id == user_id)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Already liked")

    like = Like(post_id=post_id, user_id=user_id)
    db.add(like)
    post.like_count += 1
    await db.flush()
    return like


async def remove_like(post_id: int, user_id: int, db: AsyncSession) -> None:
    existing = await db.execute(
        select(Like).where(Like.post_id == post_id, Like.user_id == user_id)
    )
    like = existing.scalar_one_or_none()
    if not like:
        return

    post_result = await db.execute(select(Post).where(Post.id == post_id))
    post = post_result.scalar_one_or_none()
    if post:
        post.like_count = max(0, post.like_count - 1)

    await db.delete(like)
    await db.flush()


async def toggle_like(post_id: int, user_id: int, db: AsyncSession) -> dict:
    post_result = await db.execute(select(Post).where(Post.id == post_id))
    post = post_result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    existing = await db.execute(
        select(Like).where(Like.post_id == post_id, Like.user_id == user_id)
    )
    like = existing.scalar_one_or_none()

    if like:
        await db.delete(like)
        post.like_count = max(0, post.like_count - 1)
        await db.flush()
        return {"liked": False, "like_count": post.like_count}

    new_like = Like(post_id=post_id, user_id=user_id)
    db.add(new_like)
    post.like_count += 1
    await db.flush()
    return {"liked": True, "like_count": post.like_count, "post_author_id": post.author_id}
