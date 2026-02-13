from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from functional_core.core.post import build_post_response, can_delete_post, extract_hashtags
from functional_core.shell.models import Hashtag, Post, PostHashtag


def _post_to_dict(post: Post) -> dict:
    return build_post_response(
        post_id=post.id,
        author_id=post.author_id,
        author_username=post.author.username if post.author else None,
        content=post.content,
        image_url=post.image_url,
        like_count=len(post.likes) if post.likes else 0,
        comment_count=len(post.comments) if post.comments else 0,
        created_at=post.created_at,
    )


async def _get_post_with_relations(db: AsyncSession, post_id: int) -> Post | None:
    result = await db.execute(
        select(Post)
        .options(selectinload(Post.author), selectinload(Post.likes), selectinload(Post.comments))
        .where(Post.id == post_id)
    )
    return result.scalar_one_or_none()


async def create_post(
    db: AsyncSession, author_id: int, content: str | None, image_url: str | None
) -> dict:
    post = Post(author_id=author_id, content=content, image_url=image_url)
    db.add(post)
    await db.flush()

    tags = extract_hashtags(content)
    for tag_name in tags:
        tag_lower = tag_name.lower()
        result = await db.execute(select(Hashtag).where(Hashtag.name == tag_lower))
        hashtag = result.scalar_one_or_none()
        if not hashtag:
            hashtag = Hashtag(name=tag_lower)
            db.add(hashtag)
            await db.flush()
            await db.refresh(hashtag)

        existing_link = await db.execute(
            select(PostHashtag).where(
                PostHashtag.post_id == post.id, PostHashtag.hashtag_id == hashtag.id
            )
        )
        if not existing_link.scalar_one_or_none():
            db.add(PostHashtag(post_id=post.id, hashtag_id=hashtag.id))
            await db.flush()

    loaded_post = await _get_post_with_relations(db, post.id)
    return _post_to_dict(loaded_post)


async def get_post(db: AsyncSession, post_id: int) -> dict:
    post = await _get_post_with_relations(db, post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return _post_to_dict(post)


async def get_posts_by_author(
    db: AsyncSession, author_id: int, limit: int = 20, offset: int = 0
) -> list[dict]:
    result = await db.execute(
        select(Post)
        .options(selectinload(Post.author), selectinload(Post.likes), selectinload(Post.comments))
        .where(Post.author_id == author_id)
        .order_by(Post.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return [_post_to_dict(p) for p in result.scalars().all()]


async def delete_post(db: AsyncSession, post_id: int, user_id: int) -> None:
    post = await _get_post_with_relations(db, post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    if not can_delete_post(post.author_id, user_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your post")

    link_result = await db.execute(select(PostHashtag).where(PostHashtag.post_id == post_id))
    for ph in link_result.scalars().all():
        await db.delete(ph)
    await db.flush()

    await db.delete(post)
    await db.flush()
