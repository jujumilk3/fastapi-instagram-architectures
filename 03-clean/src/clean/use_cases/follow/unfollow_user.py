from fastapi import HTTPException, status

from clean.use_cases.interfaces.repositories import FollowRepository


class UnfollowUserUseCase:
    def __init__(self, follow_repo: FollowRepository):
        self.follow_repo = follow_repo

    async def execute(self, follower_id: int, following_id: int) -> dict:
        if not await self.follow_repo.get(follower_id, following_id):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not following")
        await self.follow_repo.delete(follower_id, following_id)
        return {"following": False}
