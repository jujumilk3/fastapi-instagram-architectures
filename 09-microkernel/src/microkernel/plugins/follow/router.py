from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from microkernel.core.database import get_db
from microkernel.core.security import get_current_user_id
from microkernel.plugins.follow.service import FollowService

router = APIRouter(prefix="/api/follow", tags=["follow"])


@router.post("/{following_id}")
async def follow_user(following_id: int, user_id: int = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    return await FollowService(db).follow(user_id, following_id)


@router.delete("/{following_id}")
async def unfollow_user(following_id: int, user_id: int = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    return await FollowService(db).unfollow(user_id, following_id)
