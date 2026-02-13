from fastapi import HTTPException, status

from clean.use_cases.interfaces.repositories import FollowRepository, PostRepository, UserRepository


class GetProfileUseCase:
    def __init__(self, user_repo: UserRepository, follow_repo: FollowRepository, post_repo: PostRepository):
        self.user_repo = user_repo
        self.follow_repo = follow_repo
        self.post_repo = post_repo

    async def execute(self, user_id: int) -> dict:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return {
            "id": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "bio": user.bio,
            "profile_image_url": user.profile_image_url,
            "post_count": await self.post_repo.count_by_author(user_id),
            "follower_count": await self.follow_repo.count_followers(user_id),
            "following_count": await self.follow_repo.count_following(user_id),
        }
