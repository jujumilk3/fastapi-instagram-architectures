from fastapi import HTTPException, status

from clean.entities.social import Follow, Notification
from clean.use_cases.interfaces.repositories import FollowRepository, NotificationRepository, UserRepository


class FollowUserUseCase:
    def __init__(self, follow_repo: FollowRepository, user_repo: UserRepository,
                 notification_repo: NotificationRepository):
        self.follow_repo = follow_repo
        self.user_repo = user_repo
        self.notification_repo = notification_repo

    async def execute(self, follower_id: int, following_id: int) -> dict:
        if follower_id == following_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot follow yourself")
        if not await self.user_repo.get_by_id(following_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        if await self.follow_repo.get(follower_id, following_id):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Already following")
        await self.follow_repo.create(Follow(follower_id=follower_id, following_id=following_id))
        await self.notification_repo.create(Notification(
            user_id=following_id, actor_id=follower_id, type="follow", message="started following you",
        ))
        return {"following": True}
