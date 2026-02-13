from fastapi import HTTPException, status

from clean.entities.post import Like
from clean.entities.social import Notification
from clean.use_cases.interfaces.repositories import LikeRepository, NotificationRepository, PostRepository


class ToggleLikeUseCase:
    def __init__(self, like_repo: LikeRepository, post_repo: PostRepository,
                 notification_repo: NotificationRepository):
        self.like_repo = like_repo
        self.post_repo = post_repo
        self.notification_repo = notification_repo

    async def execute(self, post_id: int, user_id: int) -> dict:
        post = await self.post_repo.get_by_id(post_id)
        if not post:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
        existing = await self.like_repo.get(post_id, user_id)
        if existing:
            await self.like_repo.delete(post_id, user_id)
            liked = False
        else:
            await self.like_repo.create(Like(post_id=post_id, user_id=user_id))
            liked = True
            if post.author_id != user_id:
                await self.notification_repo.create(Notification(
                    user_id=post.author_id, actor_id=user_id, type="like",
                    reference_id=post_id, message="liked your post",
                ))
        count = await self.like_repo.count_by_post(post_id)
        return {"liked": liked, "like_count": count}
