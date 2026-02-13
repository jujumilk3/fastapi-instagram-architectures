from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from layered.models.like import Like
from layered.models.notification import Notification
from layered.repositories.like import LikeRepository
from layered.repositories.notification import NotificationRepository
from layered.repositories.post import PostRepository


class LikeService:
    def __init__(self, db: AsyncSession):
        self.like_repo = LikeRepository(db)
        self.post_repo = PostRepository(db)
        self.notification_repo = NotificationRepository(db)

    async def toggle(self, post_id: int, user_id: int) -> dict:
        post = await self.post_repo.get_by_id(post_id)
        if not post:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

        existing = await self.like_repo.get(post_id, user_id)
        if existing:
            await self.like_repo.delete(existing)
            liked = False
        else:
            await self.like_repo.create(Like(post_id=post_id, user_id=user_id))
            liked = True

            if post.author_id != user_id:
                await self.notification_repo.create(
                    Notification(
                        user_id=post.author_id,
                        actor_id=user_id,
                        type="like",
                        reference_id=post_id,
                        message=f"liked your post",
                    )
                )

        count = await self.like_repo.count_by_post(post_id)
        return {"liked": liked, "like_count": count}
