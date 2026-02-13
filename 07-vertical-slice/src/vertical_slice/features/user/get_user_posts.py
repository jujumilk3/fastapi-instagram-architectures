from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from vertical_slice.models.tables import Comment, Like, Post, User


@dataclass
class GetUserPostsRequest:
    user_id: int
    limit: int
    offset: int
    db: AsyncSession


@dataclass
class PostItem:
    id: int
    author_id: int
    author_username: str | None
    content: str | None
    image_url: str | None
    like_count: int
    comment_count: int
    created_at: datetime


async def get_user_posts_handler(request: GetUserPostsRequest) -> list[PostItem]:
    db = request.db
    result = await db.execute(
        select(Post)
        .where(Post.author_id == request.user_id)
        .order_by(Post.created_at.desc())
        .limit(request.limit)
        .offset(request.offset)
    )
    posts = []
    for post in result.scalars().all():
        user = await db.get(User, post.author_id)
        like_count = (await db.execute(
            select(func.count()).select_from(Like).where(Like.post_id == post.id)
        )).scalar_one()
        comment_count = (await db.execute(
            select(func.count()).select_from(Comment).where(Comment.post_id == post.id)
        )).scalar_one()
        posts.append(PostItem(
            id=post.id,
            author_id=post.author_id,
            author_username=user.username if user else None,
            content=post.content,
            image_url=post.image_url,
            like_count=like_count,
            comment_count=comment_count,
            created_at=post.created_at,
        ))
    return posts
