from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from vertical_slice.models.tables import Comment, Like, Post, User


@dataclass
class GetPostRequest:
    post_id: int
    db: AsyncSession


@dataclass
class GetPostResponse:
    id: int
    author_id: int
    author_username: str | None
    content: str | None
    image_url: str | None
    like_count: int
    comment_count: int
    created_at: datetime


async def get_post_handler(request: GetPostRequest) -> GetPostResponse:
    db = request.db
    post = await db.get(Post, request.post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    user = await db.get(User, post.author_id)
    like_count = (await db.execute(
        select(func.count()).select_from(Like).where(Like.post_id == post.id)
    )).scalar_one()
    comment_count = (await db.execute(
        select(func.count()).select_from(Comment).where(Comment.post_id == post.id)
    )).scalar_one()

    return GetPostResponse(
        id=post.id,
        author_id=post.author_id,
        author_username=user.username if user else None,
        content=post.content,
        image_url=post.image_url,
        like_count=like_count,
        comment_count=comment_count,
        created_at=post.created_at,
    )
