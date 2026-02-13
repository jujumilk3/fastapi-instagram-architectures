from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from vertical_slice.models.tables import Comment, User


@dataclass
class GetCommentsRequest:
    post_id: int
    limit: int
    offset: int
    db: AsyncSession


@dataclass
class CommentItem:
    id: int
    post_id: int
    author_id: int
    author_username: str | None
    content: str
    created_at: datetime


async def get_comments_handler(request: GetCommentsRequest) -> list[CommentItem]:
    db = request.db
    result = await db.execute(
        select(Comment)
        .where(Comment.post_id == request.post_id)
        .order_by(Comment.created_at.desc())
        .limit(request.limit)
        .offset(request.offset)
    )
    comments = []
    for c in result.scalars().all():
        user = await db.get(User, c.author_id)
        comments.append(CommentItem(
            id=c.id,
            post_id=c.post_id,
            author_id=c.author_id,
            author_username=user.username if user else None,
            content=c.content,
            created_at=c.created_at,
        ))
    return comments
