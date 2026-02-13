from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from modular_monolith.modules.auth.schemas import LoginRequest, TokenResponse, UserCreate, UserResponse
from modular_monolith.modules.auth.service import AuthService
from modular_monolith.shared.database import get_db
from modular_monolith.shared.security import get_current_user_id

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(data: UserCreate, db: AsyncSession = Depends(get_db)):
    return await AuthService(db).register(data)


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    return await AuthService(db).login(data)


@router.get("/me", response_model=UserResponse)
async def me(user_id: int = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    return await AuthService(db).get_me(user_id)
