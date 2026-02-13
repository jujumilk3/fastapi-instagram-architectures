from clean.entities.social import Hashtag
from clean.use_cases.interfaces.repositories import HashtagRepository


class SearchHashtagsUseCase:
    def __init__(self, hashtag_repo: HashtagRepository):
        self.hashtag_repo = hashtag_repo

    async def execute(self, query: str, limit: int = 20) -> list[Hashtag]:
        return await self.hashtag_repo.search(query, limit)
