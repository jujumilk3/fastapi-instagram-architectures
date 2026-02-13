from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from layered.database import get_db
from layered.schemas.post import PostResponse
from layered.schemas.user import UserProfileResponse, UserResponse, UserUpdate
from layered.security import get_current_user_id
from layered.services.post import PostService
from layered.services.user import UserService

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/{user_id}", response_model=UserProfileResponse)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    return await UserService(db).get_profile(user_id)


@router.put("/me", response_model=UserResponse)
async def update_me(
    data: UserUpdate,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    return await UserService(db).update_me(user_id, data)


@router.get("/{user_id}/posts", response_model=list[PostResponse])
async def get_user_posts(user_id: int, limit: int = 20, offset: int = 0, db: AsyncSession = Depends(get_db)):
    return await PostService(db).get_by_author(user_id, limit, offset)


@router.get("/{user_id}/followers", response_model=list[UserResponse])
async def get_followers(user_id: int, db: AsyncSession = Depends(get_db)):
    return await UserService(db).get_followers(user_id)


@router.get("/{user_id}/following", response_model=list[UserResponse])
async def get_following(user_id: int, db: AsyncSession = Depends(get_db)):
    return await UserService(db).get_following(user_id)
