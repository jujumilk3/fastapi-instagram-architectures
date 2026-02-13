from __future__ import annotations

from fastapi import HTTPException, status

from ddd.domain.user.aggregate import UserAggregate
from ddd.domain.user.repository import UserRepository
from ddd.infrastructure.security import SecurityProvider


class AuthApplicationService:
    def __init__(self, user_repo: UserRepository, security: SecurityProvider):
        self.user_repo = user_repo
        self.security = security

    async def register(
        self,
        username: str,
        email: str,
        password: str,
        full_name: str | None = None,
    ) -> UserAggregate:
        if await self.user_repo.get_by_email(email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )
        if await self.user_repo.get_by_username(username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken",
            )
        user = UserAggregate.create(
            username=username,
            email=email,
            hashed_password=self.security.hash_password(password),
            full_name=full_name,
        )
        saved = await self.user_repo.create(user)
        saved.collect_events()
        return saved

    async def login(self, email: str, password: str) -> str:
        user = await self.user_repo.get_by_email(email)
        if not user or not self.security.verify_password(
            password, user.hashed_password
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )
        return self.security.create_token({"sub": str(user.id)})

    async def get_me(self, user_id: int) -> UserAggregate:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        return user
