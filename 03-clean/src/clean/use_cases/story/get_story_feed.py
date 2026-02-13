from clean.use_cases.interfaces.repositories import FollowRepository, StoryRepository, UserRepository
from clean.use_cases.story.get_my_stories import _enrich_story


class GetStoryFeedUseCase:
    def __init__(self, story_repo: StoryRepository, follow_repo: FollowRepository,
                 user_repo: UserRepository):
        self.story_repo = story_repo
        self.follow_repo = follow_repo
        self.user_repo = user_repo

    async def execute(self, user_id: int) -> list[dict]:
        ids = await self.follow_repo.get_following(user_id)
        ids.append(user_id)
        stories = await self.story_repo.get_feed(ids)
        return [await _enrich_story(s, self.user_repo) for s in stories]
