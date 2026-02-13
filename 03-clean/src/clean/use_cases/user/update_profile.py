from fastapi import HTTPException, status

from clean.entities.user import User
from clean.use_cases.interfaces.repositories import UserRepository


class UpdateProfileUseCase:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def execute(self, user_id: int, **kwargs) -> User:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        for key, value in kwargs.items():
            if value is not None:
                setattr(user, key, value)
        return await self.user_repo.update(user)
