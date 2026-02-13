from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from event_driven.events.definitions import POST_LIKED, POST_UNLIKED
from event_driven.models.tables import Like, Post
from event_driven.shared.event_broker import broker


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
        await broker.publish(POST_UNLIKED, {
            "post_id": post_id,
            "user_id": user_id,
            "post_author_id": post.author_id,
            "db": db,
        })
        return {"liked": False, "like_count": post.like_count}

    new_like = Like(post_id=post_id, user_id=user_id)
    db.add(new_like)
    post.like_count += 1
    await db.flush()

    await broker.publish(POST_LIKED, {
        "post_id": post_id,
        "user_id": user_id,
        "post_author_id": post.author_id,
        "db": db,
    })

    return {"liked": True, "like_count": post.like_count}
