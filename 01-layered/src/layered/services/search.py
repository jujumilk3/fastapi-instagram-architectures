from sqlalchemy.ext.asyncio import AsyncSession

from layered.repositories.hashtag import HashtagRepository
from layered.repositories.user import UserRepository
from layered.schemas.hashtag import HashtagResponse
from layered.schemas.post import PostResponse
from layered.schemas.user import UserResponse
from layered.services.post import _post_to_response


class SearchService:
    def __init__(self, db: AsyncSession):
        self.user_repo = UserRepository(db)
        self.hashtag_repo = HashtagRepository(db)

    async def search_users(self, query: str, limit: int = 20) -> list[UserResponse]:
        users = await self.user_repo.search(query, limit)
        return [UserResponse.model_validate(u) for u in users]

    async def search_hashtags(self, query: str, limit: int = 20) -> list[HashtagResponse]:
        hashtags = await self.hashtag_repo.search(query, limit)
        return [HashtagResponse.model_validate(h) for h in hashtags]

    async def get_posts_by_hashtag(self, tag: str, limit: int = 20, offset: int = 0) -> list[PostResponse]:
        posts = await self.hashtag_repo.get_posts_by_hashtag(tag, limit, offset)
        return [_post_to_response(p) for p in posts]
