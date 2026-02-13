import re

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from event_driven.models.tables import Hashtag, PostHashtag

HASHTAG_PATTERN = re.compile(r"#(\w+)")


async def on_post_created(event_data: dict) -> None:
    db: AsyncSession = event_data["db"]
    content = event_data.get("content") or ""
    post_id = event_data["post_id"]

    tags = HASHTAG_PATTERN.findall(content)
    if not tags:
        return

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

    await db.flush()
