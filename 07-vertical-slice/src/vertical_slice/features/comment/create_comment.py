from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from vertical_slice.models.tables import Comment, Notification, Post


@dataclass
class CreateCommentRequest:
    post_id: int
    author_id: int
    content: str
    db: AsyncSession


@dataclass
class CreateCommentResponse:
    id: int
    post_id: int
    author_id: int
    author_username: str | None
    content: str
    created_at: datetime


async def create_comment_handler(request: CreateCommentRequest) -> CreateCommentResponse:
    db = request.db
    post = await db.get(Post, request.post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    comment = Comment(post_id=request.post_id, author_id=request.author_id, content=request.content)
    db.add(comment)
    await db.flush()
    await db.refresh(comment)

    if post.author_id != request.author_id:
        db.add(Notification(
            user_id=post.author_id,
            actor_id=request.author_id,
            type="comment",
            reference_id=request.post_id,
            message="commented on your post",
        ))
        await db.flush()

    return CreateCommentResponse(
        id=comment.id,
        post_id=comment.post_id,
        author_id=comment.author_id,
        author_username=None,
        content=comment.content,
        created_at=comment.created_at,
    )
