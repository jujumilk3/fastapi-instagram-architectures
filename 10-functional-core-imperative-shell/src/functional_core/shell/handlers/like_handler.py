from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from functional_core.core.like import determine_like_action
from functional_core.core.notification import create_notification_data
from functional_core.shell.models import Like, Notification, Post


async def toggle_like(db: AsyncSession, post_id: int, user_id: int) -> dict:
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    existing_result = await db.execute(
        select(Like).where(Like.post_id == post_id, Like.user_id == user_id)
    )
    existing = existing_result.scalar_one_or_none()

    action = determine_like_action(existing is not None)

    if action == "remove":
        await db.delete(existing)
        liked = False
    else:
        db.add(Like(post_id=post_id, user_id=user_id))
        liked = True

        if post.author_id != user_id:
            notif_data = create_notification_data("like", user_id, post.author_id, post_id)
            db.add(Notification(**notif_data))

    await db.flush()

    count_result = await db.execute(
        select(func.count()).select_from(Like).where(Like.post_id == post_id)
    )
    return {"liked": liked, "like_count": count_result.scalar_one()}
