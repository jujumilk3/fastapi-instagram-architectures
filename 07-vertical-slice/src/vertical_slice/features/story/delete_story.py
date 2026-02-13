from __future__ import annotations

from dataclasses import dataclass

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from vertical_slice.models.tables import Story


@dataclass
class DeleteStoryRequest:
    story_id: int
    user_id: int
    db: AsyncSession


async def delete_story_handler(request: DeleteStoryRequest) -> None:
    db = request.db
    story = await db.get(Story, request.story_id)
    if not story:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Story not found")
    if story.author_id != request.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your story")
    await db.delete(story)
    await db.flush()
