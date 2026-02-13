from clean.entities.social import Story
from clean.use_cases.interfaces.repositories import StoryRepository, UserRepository


async def _enrich_story(story: Story, user_repo: UserRepository) -> dict:
    author = await user_repo.get_by_id(story.author_id)
    return {
        "id": story.id, "author_id": story.author_id,
        "author_username": author.username if author else None,
        "image_url": story.image_url, "content": story.content,
        "created_at": story.created_at,
    }


class GetMyStoriesUseCase:
    def __init__(self, story_repo: StoryRepository, user_repo: UserRepository):
        self.story_repo = story_repo
        self.user_repo = user_repo

    async def execute(self, user_id: int) -> list[dict]:
        stories = await self.story_repo.get_active_by_author(user_id)
        return [await _enrich_story(s, self.user_repo) for s in stories]
