from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from functional_core.core.post import build_post_response
from functional_core.shell.models import Hashtag, Post, PostHashtag, User


async def search_users(db: AsyncSession, query: str, limit: int = 20) -> list[User]:
    result = await db.execute(
        select(User).where(User.username.ilike(f"%{query}%")).limit(limit)
    )
    return list(result.scalars().all())


async def search_hashtags(db: AsyncSession, query: str, limit: int = 20) -> list[Hashtag]:
    result = await db.execute(
        select(Hashtag).where(Hashtag.name.ilike(f"%{query}%")).limit(limit)
    )
    return list(result.scalars().all())


async def get_posts_by_hashtag(
    db: AsyncSession, tag: str, limit: int = 20, offset: int = 0
) -> list[dict]:
    result = await db.execute(
        select(Post)
        .join(PostHashtag, Post.id == PostHashtag.post_id)
        .join(Hashtag, PostHashtag.hashtag_id == Hashtag.id)
        .options(selectinload(Post.author), selectinload(Post.likes), selectinload(Post.comments))
        .where(Hashtag.name == tag)
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
