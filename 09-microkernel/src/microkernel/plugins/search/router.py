from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from microkernel.core.database import get_db
from microkernel.plugins.post.schemas import PostResponse
from microkernel.plugins.search.service import HashtagResponse, SearchService
from microkernel.plugins.user.schemas import UserResponse

router = APIRouter(prefix="/api/search", tags=["search"])


@router.get("/users", response_model=list[UserResponse])
async def search_users(q: str, limit: int = 20, db: AsyncSession = Depends(get_db)):
    return await SearchService(db).search_users(q, limit)


@router.get("/hashtags", response_model=list[HashtagResponse])
async def search_hashtags(q: str, limit: int = 20, db: AsyncSession = Depends(get_db)):
    return await SearchService(db).search_hashtags(q, limit)


@router.get("/posts/hashtag/{tag}", response_model=list[PostResponse])
async def get_posts_by_hashtag(tag: str, limit: int = 20, offset: int = 0, db: AsyncSession = Depends(get_db)):
    return await SearchService(db).get_posts_by_hashtag(tag, limit, offset)
