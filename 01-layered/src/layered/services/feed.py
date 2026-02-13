from sqlalchemy.ext.asyncio import AsyncSession

from layered.repositories.follow import FollowRepository
from layered.repositories.post import PostRepository
from layered.schemas.post import PostResponse
from layered.services.post import _post_to_response


class FeedService:
    def __init__(self, db: AsyncSession):
        self.post_repo = PostRepository(db)
        self.follow_repo = FollowRepository(db)

    async def get_feed(self, user_id: int, limit: int = 20, offset: int = 0) -> list[PostResponse]:
        following_ids = await self.follow_repo.get_following(user_id)
        # Include own posts in feed
        following_ids.append(user_id)
        posts = await self.post_repo.get_feed(following_ids, limit, offset)
        return [_post_to_response(p) for p in posts]
