from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from modular_monolith.modules.auth.models import User
from modular_monolith.modules.post.models import Hashtag, Post, PostHashtag
from modular_monolith.modules.post.schemas import PostResponse
from modular_monolith.modules.post.service import PostService
from modular_monolith.modules.user.schemas import UserResponse

from pydantic import BaseModel


class HashtagResponse(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


class SearchService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def search_users(self, query: str, limit: int = 20) -> list[UserResponse]:
        result = await self.db.execute(
            select(User).where(User.username.ilike(f"%{query}%")).limit(limit)
        )
        return [UserResponse.model_validate(u) for u in result.scalars().all()]

    async def search_hashtags(self, query: str, limit: int = 20) -> list[HashtagResponse]:
        result = await self.db.execute(
            select(Hashtag).where(Hashtag.name.ilike(f"%{query}%")).limit(limit)
        )
        return [HashtagResponse.model_validate(h) for h in result.scalars().all()]

    async def get_posts_by_hashtag(self, tag: str, limit: int = 20, offset: int = 0) -> list[PostResponse]:
        result = await self.db.execute(
            select(Post)
            .join(PostHashtag, Post.id == PostHashtag.post_id)
            .join(Hashtag, PostHashtag.hashtag_id == Hashtag.id)
            .where(Hashtag.name == tag)
            .order_by(Post.created_at.desc())
            .limit(limit).offset(offset)
        )
        post_service = PostService(self.db)
        return [await post_service._to_response(p) for p in result.scalars().all()]
