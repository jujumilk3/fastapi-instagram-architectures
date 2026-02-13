from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from event_driven.models.tables import Comment, Post, User


async def get_post(post_id: int, db: AsyncSession) -> dict | None:
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()
    if not post:
        return None

    user_result = await db.execute(select(User.username).where(User.id == post.author_id))
    username = user_result.scalar_one_or_none()

    return {
        "id": post.id,
        "author_id": post.author_id,
        "author_username": username,
        "content": post.content,
        "image_url": post.image_url,
        "like_count": post.like_count,
        "comment_count": post.comment_count,
        "created_at": post.created_at,
    }


async def get_user_posts(
    user_id: int, limit: int, offset: int, db: AsyncSession
) -> list[dict]:
    result = await db.execute(
        select(Post)
        .where(Post.author_id == user_id)
        .order_by(Post.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    posts = result.scalars().all()

    user_result = await db.execute(select(User.username).where(User.id == user_id))
    username = user_result.scalar_one_or_none()

    return [
        {
            "id": p.id,
            "author_id": p.author_id,
            "author_username": username,
            "content": p.content,
            "image_url": p.image_url,
            "like_count": p.like_count,
            "comment_count": p.comment_count,
            "created_at": p.created_at,
        }
        for p in posts
    ]


async def get_post_comments(
    post_id: int, limit: int, offset: int, db: AsyncSession
) -> list[dict]:
    result = await db.execute(
        select(Comment, User.username)
        .outerjoin(User, Comment.author_id == User.id)
        .where(Comment.post_id == post_id)
        .order_by(Comment.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    rows = result.all()
    return [
        {
            "id": comment.id,
            "post_id": comment.post_id,
            "author_id": comment.author_id,
            "author_username": username,
            "content": comment.content,
            "created_at": comment.created_at,
        }
        for comment, username in rows
    ]
