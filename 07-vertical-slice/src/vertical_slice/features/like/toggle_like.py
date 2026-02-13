from __future__ import annotations

from dataclasses import dataclass

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from vertical_slice.models.tables import Like, Notification, Post


@dataclass
class ToggleLikeRequest:
    post_id: int
    user_id: int
    db: AsyncSession


@dataclass
class ToggleLikeResponse:
    liked: bool
    like_count: int


async def toggle_like_handler(request: ToggleLikeRequest) -> ToggleLikeResponse:
    db = request.db
    post = await db.get(Post, request.post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    result = await db.execute(
        select(Like).where(Like.post_id == request.post_id, Like.user_id == request.user_id)
    )
    existing = result.scalar_one_or_none()

    if existing:
        await db.delete(existing)
        liked = False
    else:
        db.add(Like(post_id=request.post_id, user_id=request.user_id))
        liked = True
        if post.author_id != request.user_id:
            db.add(Notification(
                user_id=post.author_id,
                actor_id=request.user_id,
                type="like",
                reference_id=request.post_id,
                message="liked your post",
            ))

    await db.flush()
    count = (await db.execute(
        select(func.count()).select_from(Like).where(Like.post_id == request.post_id)
    )).scalar_one()

    return ToggleLikeResponse(liked=liked, like_count=count)
