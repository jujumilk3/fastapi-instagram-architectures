from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from saga_choreography.models.tables import Follow, Post, User


async def get_feed(
    user_id: int, limit: int, offset: int, db: AsyncSession
) -> list[dict]:
    following_result = await db.execute(
        select(Follow.following_id).where(Follow.follower_id == user_id)
    )
    following_ids = [row[0] for row in following_result.all()]
    following_ids.append(user_id)

    result = await db.execute(
        select(Post, User.username)
        .outerjoin(User, Post.author_id == User.id)
        .where(Post.author_id.in_(following_ids))
        .order_by(Post.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    rows = result.all()
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
