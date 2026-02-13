from fastapi import HTTPException, status

from clean.entities.user import User
from clean.use_cases.interfaces.repositories import UserRepository
from clean.use_cases.interfaces.security import SecurityGateway


class RegisterUseCase:
    def __init__(self, user_repo: UserRepository, security: SecurityGateway):
        self.user_repo = user_repo
        self.security = security

    async def execute(self, username: str, email: str, password: str, full_name: str | None = None) -> User:
        if await self.user_repo.get_by_email(email):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
        if await self.user_repo.get_by_username(username):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken")
        user = User(
            username=username,
            email=email,
            hashed_password=self.security.hash_password(password),
            full_name=full_name,
        )
        return await self.user_repo.create(user)
