from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from saga_choreography.models.tables import Post, User


async def create_post(
    author_id: int,
    content: str | None,
    image_url: str | None,
    db: AsyncSession,
) -> Post:
    user_result = await db.execute(select(User).where(User.id == author_id))
    user = user_result.scalar_one_or_none()

    post = Post(author_id=author_id, content=content, image_url=image_url)
    db.add(post)

    if user:
        user.post_count += 1

    await db.flush()
    return post


async def delete_post(post_id: int, user_id: int, db: AsyncSession) -> None:
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    if post.author_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your post")

    user_result = await db.execute(select(User).where(User.id == user_id))
    user = user_result.scalar_one_or_none()
    if user and user.post_count > 0:
        user.post_count -= 1

    await db.delete(post)
    await db.flush()


async def delete_post_by_id(post_id: int, db: AsyncSession) -> None:
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()
    if post:
        user_result = await db.execute(select(User).where(User.id == post.author_id))
        user = user_result.scalar_one_or_none()
        if user and user.post_count > 0:
            user.post_count -= 1
        await db.delete(post)
        await db.flush()


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
    from saga_choreography.models.tables import Comment

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
