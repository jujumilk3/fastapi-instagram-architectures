from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from vertical_slice.models.tables import Hashtag


@dataclass
class SearchHashtagsRequest:
    query: str
    limit: int
    db: AsyncSession


@dataclass
class HashtagItem:
    id: int
    name: str


async def search_hashtags_handler(request: SearchHashtagsRequest) -> list[HashtagItem]:
    db = request.db
    result = await db.execute(
        select(Hashtag).where(Hashtag.name.ilike(f"%{request.query}%")).limit(request.limit)
    )
    return [HashtagItem(id=h.id, name=h.name) for h in result.scalars().all()]
