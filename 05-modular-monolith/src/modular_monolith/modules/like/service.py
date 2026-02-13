from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from modular_monolith.modules.like.models import Like
from modular_monolith.modules.notification.service import NotificationService
from modular_monolith.modules.post.models import Post


class LikeService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def toggle(self, post_id: int, user_id: int) -> dict:
        post = await self.db.get(Post, post_id)
        if not post:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

        result = await self.db.execute(
            select(Like).where(Like.post_id == post_id, Like.user_id == user_id)
        )
        existing = result.scalar_one_or_none()

        if existing:
            await self.db.delete(existing)
            liked = False
        else:
            self.db.add(Like(post_id=post_id, user_id=user_id))
            liked = True
            if post.author_id != user_id:
                await NotificationService(self.db).create_notification(
                    user_id=post.author_id, actor_id=user_id,
                    type="like", reference_id=post_id, message="liked your post",
                )

        await self.db.flush()
        count = (await self.db.execute(
            select(func.count()).select_from(Like).where(Like.post_id == post_id)
        )).scalar_one()
        return {"liked": liked, "like_count": count}
