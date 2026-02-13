from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from microkernel.core.database import get_db
from microkernel.core.security import get_current_user_id
from microkernel.plugins.feed.service import FeedService
from microkernel.plugins.post.schemas import PostResponse

router = APIRouter(prefix="/api/feed", tags=["feed"])


@router.get("", response_model=list[PostResponse])
async def get_feed(limit: int = 20, offset: int = 0, user_id: int = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    return await FeedService(db).get_feed(user_id, limit, offset)
