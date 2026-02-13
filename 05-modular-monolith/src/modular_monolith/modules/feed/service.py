from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from modular_monolith.modules.follow.models import Follow
from modular_monolith.modules.post.models import Post
from modular_monolith.modules.post.schemas import PostResponse
from modular_monolith.modules.post.service import PostService


class FeedService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_feed(self, user_id: int, limit: int = 20, offset: int = 0) -> list[PostResponse]:
        result = await self.db.execute(
            select(Follow.following_id).where(Follow.follower_id == user_id)
        )
        following_ids = list(result.scalars().all())
        following_ids.append(user_id)

        result = await self.db.execute(
            select(Post).where(Post.author_id.in_(following_ids)).order_by(Post.created_at.desc()).limit(limit).offset(offset)
        )
        post_service = PostService(self.db)
        return [await post_service._to_response(p) for p in result.scalars().all()]
