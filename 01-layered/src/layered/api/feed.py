from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from layered.database import get_db
from layered.schemas.post import PostResponse
from layered.security import get_current_user_id
from layered.services.feed import FeedService

router = APIRouter(prefix="/api/feed", tags=["feed"])


@router.get("", response_model=list[PostResponse])
async def get_feed(
    limit: int = 20,
    offset: int = 0,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    return await FeedService(db).get_feed(user_id, limit, offset)
