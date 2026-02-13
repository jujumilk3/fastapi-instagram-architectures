from clean.entities.user import User
from clean.use_cases.interfaces.repositories import UserRepository


class SearchUsersUseCase:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def execute(self, query: str, limit: int = 20) -> list[User]:
        return await self.user_repo.search(query, limit)
