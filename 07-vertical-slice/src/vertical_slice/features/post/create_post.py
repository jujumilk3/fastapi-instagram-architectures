from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from vertical_slice.models.tables import Comment, Hashtag, Like, Post, PostHashtag, User


@dataclass
class CreatePostRequest:
    author_id: int
    content: str | None
    image_url: str | None
    db: AsyncSession


@dataclass
class CreatePostResponse:
    id: int
    author_id: int
    author_username: str | None
    content: str | None
    image_url: str | None
    like_count: int
    comment_count: int
    created_at: datetime


def _extract_hashtags(text: str | None) -> list[str]:
    if not text:
        return []
    return re.findall(r"#(\w+)", text)


async def create_post_handler(request: CreatePostRequest) -> CreatePostResponse:
    db = request.db

    post = Post(author_id=request.author_id, content=request.content, image_url=request.image_url)
    db.add(post)
    await db.flush()
    await db.refresh(post)

    for tag in _extract_hashtags(request.content):
        tag_lower = tag.lower()
        result = await db.execute(select(Hashtag).where(Hashtag.name == tag_lower))
        hashtag = result.scalar_one_or_none()
        if not hashtag:
            hashtag = Hashtag(name=tag_lower)
            db.add(hashtag)
            await db.flush()
            await db.refresh(hashtag)
        db.add(PostHashtag(post_id=post.id, hashtag_id=hashtag.id))
    await db.flush()

    user = await db.get(User, post.author_id)
    like_count = (await db.execute(
        select(func.count()).select_from(Like).where(Like.post_id == post.id)
    )).scalar_one()
    comment_count = (await db.execute(
        select(func.count()).select_from(Comment).where(Comment.post_id == post.id)
    )).scalar_one()

    return CreatePostResponse(
        id=post.id,
        author_id=post.author_id,
        author_username=user.username if user else None,
        content=post.content,
        image_url=post.image_url,
        like_count=like_count,
        comment_count=comment_count,
        created_at=post.created_at,
    )
