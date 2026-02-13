from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from microkernel.core.database import get_db
from microkernel.core.security import get_current_user_id
from microkernel.plugins.post.schemas import PostResponse
from microkernel.plugins.post.service import PostService
from microkernel.plugins.user.schemas import UserProfileResponse, UserResponse, UserUpdate
from microkernel.plugins.user.service import UserService

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/{user_id}", response_model=UserProfileResponse)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    return await UserService(db).get_profile(user_id)


@router.put("/me", response_model=UserResponse)
async def update_me(data: UserUpdate, user_id: int = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
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
