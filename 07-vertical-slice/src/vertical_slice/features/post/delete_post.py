from __future__ import annotations

from dataclasses import dataclass

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from vertical_slice.models.tables import Post, PostHashtag


@dataclass
class DeletePostRequest:
    post_id: int
    user_id: int
    db: AsyncSession


async def delete_post_handler(request: DeletePostRequest) -> None:
    db = request.db
    post = await db.get(Post, request.post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    if post.author_id != request.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your post")

    result = await db.execute(select(PostHashtag).where(PostHashtag.post_id == request.post_id))
    for ph in result.scalars().all():
        await db.delete(ph)
    await db.delete(post)
    await db.flush()
