from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from saga_choreography.models.tables import Hashtag, Post, PostHashtag, User


async def search_users(query: str, limit: int, db: AsyncSession) -> list[dict]:
    result = await db.execute(
        select(User)
        .where(User.username.ilike(f"%{query}%"))
        .limit(limit)
    )
    users = result.scalars().all()
    return [
        {
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "full_name": u.full_name,
            "bio": u.bio,
            "profile_image_url": u.profile_image_url,
            "is_active": u.is_active,
            "created_at": u.created_at,
        }
        for u in users
    ]


async def search_hashtags(query: str, limit: int, db: AsyncSession) -> list[dict]:
    result = await db.execute(
        select(Hashtag)
        .where(Hashtag.name.ilike(f"%{query}%"))
        .limit(limit)
    )
    hashtags = result.scalars().all()
    return [{"id": h.id, "name": h.name} for h in hashtags]


async def get_posts_by_hashtag(
    tag: str, limit: int, offset: int, db: AsyncSession
) -> list[dict]:
    result = await db.execute(
        select(Hashtag).where(Hashtag.name == tag.lower())
    )
    hashtag = result.scalar_one_or_none()
    if not hashtag:
        return []

    post_ids_result = await db.execute(
        select(PostHashtag.post_id).where(PostHashtag.hashtag_id == hashtag.id)
    )
    post_ids = [row[0] for row in post_ids_result.all()]
    if not post_ids:
        return []

    posts_result = await db.execute(
        select(Post, User.username)
        .outerjoin(User, Post.author_id == User.id)
        .where(Post.id.in_(post_ids))
        .order_by(Post.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    rows = posts_result.all()
    return [
        {
            "id": post.id,
            "author_id": post.author_id,
            "author_username": username,
            "content": post.content,
            "image_url": post.image_url,
            "like_count": post.like_count,
            "comment_count": post.comment_count,
            "created_at": post.created_at,
        }
        for post, username in rows
    ]
