from clean.entities.user import User
from clean.use_cases.interfaces.repositories import FollowRepository, UserRepository


class GetFollowersUseCase:
    def __init__(self, user_repo: UserRepository, follow_repo: FollowRepository):
        self.user_repo = user_repo
        self.follow_repo = follow_repo

    async def execute(self, user_id: int) -> list[User]:
        ids = await self.follow_repo.get_followers(user_id)
        users = []
        for uid in ids:
            u = await self.user_repo.get_by_id(uid)
            if u:
                users.append(u)
        return users
