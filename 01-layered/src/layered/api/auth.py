from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from layered.database import get_db
from layered.schemas.user import LoginRequest, TokenResponse, UserCreate, UserResponse
from layered.security import get_current_user_id
from layered.services.auth import AuthService

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
