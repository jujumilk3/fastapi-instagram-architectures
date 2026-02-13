from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from layered.database import get_db
from layered.security import get_current_user_id
from layered.services.follow import FollowService

router = APIRouter(prefix="/api/follow", tags=["follow"])


@router.post("/{following_id}")
async def follow_user(
    following_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    return await FollowService(db).follow(user_id, following_id)


@router.delete("/{following_id}")
async def unfollow_user(
    following_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    return await FollowService(db).unfollow(user_id, following_id)
