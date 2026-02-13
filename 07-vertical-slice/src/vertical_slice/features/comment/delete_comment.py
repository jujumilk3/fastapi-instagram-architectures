from __future__ import annotations

from dataclasses import dataclass

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from vertical_slice.models.tables import Comment


@dataclass
class DeleteCommentRequest:
    comment_id: int
    user_id: int
    db: AsyncSession


async def delete_comment_handler(request: DeleteCommentRequest) -> None:
    db = request.db
    comment = await db.get(Comment, request.comment_id)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    if comment.author_id != request.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your comment")
    await db.delete(comment)
    await db.flush()
