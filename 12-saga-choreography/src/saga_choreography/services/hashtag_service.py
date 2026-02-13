import re

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from saga_choreography.models.tables import Hashtag, PostHashtag

HASHTAG_PATTERN = re.compile(r"#(\w+)")


async def extract_and_save(post_id: int, content: str | None, db: AsyncSession) -> list[int]:
    tags = HASHTAG_PATTERN.findall(content or "")
    if not tags:
        return []

    hashtag_ids: list[int] = []
    for tag_name in set(tags):
        tag_lower = tag_name.lower()
        result = await db.execute(select(Hashtag).where(Hashtag.name == tag_lower))
        hashtag = result.scalar_one_or_none()
        if not hashtag:
            hashtag = Hashtag(name=tag_lower)
            db.add(hashtag)
            await db.flush()

        existing = await db.execute(
            select(PostHashtag).where(
                PostHashtag.post_id == post_id,
                PostHashtag.hashtag_id == hashtag.id,
            )
        )
        if not existing.scalar_one_or_none():
            db.add(PostHashtag(post_id=post_id, hashtag_id=hashtag.id))
            hashtag_ids.append(hashtag.id)

    await db.flush()
    return hashtag_ids


async def delete_post_hashtags(post_id: int, db: AsyncSession) -> None:
    result = await db.execute(
        select(PostHashtag).where(PostHashtag.post_id == post_id)
    )
    for ph in result.scalars().all():
        await db.delete(ph)
    await db.flush()
