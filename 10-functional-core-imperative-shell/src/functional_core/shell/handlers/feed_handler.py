from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from functional_core.core.post import build_post_response
from functional_core.shell.models import Follow, Post


async def get_feed(
    db: AsyncSession, user_id: int, limit: int = 20, offset: int = 0
) -> list[dict]:
    following_result = await db.execute(
        select(Follow.following_id).where(Follow.follower_id == user_id)
    )
    following_ids = list(following_result.scalars().all())
    following_ids.append(user_id)

    result = await db.execute(
        select(Post)
        .options(selectinload(Post.author), selectinload(Post.likes), selectinload(Post.comments))
        .where(Post.author_id.in_(following_ids))
        .order_by(Post.created_at.desc())
        .limit(limit)
        .offset(offset)
    )

    return [
        build_post_response(
            post_id=p.id,
            author_id=p.author_id,
            author_username=p.author.username if p.author else None,
            content=p.content,
            image_url=p.image_url,
            like_count=len(p.likes) if p.likes else 0,
            comment_count=len(p.comments) if p.comments else 0,
            created_at=p.created_at,
        )
        for p in result.scalars().all()
    ]
