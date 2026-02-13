from fastapi import HTTPException, status

from clean.use_cases.interfaces.repositories import UserRepository
from clean.use_cases.interfaces.security import SecurityGateway


class LoginUseCase:
    def __init__(self, user_repo: UserRepository, security: SecurityGateway):
        self.user_repo = user_repo
        self.security = security

    async def execute(self, email: str, password: str) -> str:
        user = await self.user_repo.get_by_email(email)
        if not user or not self.security.verify_password(password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        return self.security.create_token({"sub": str(user.id)})
