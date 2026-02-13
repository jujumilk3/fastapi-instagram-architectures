from clean.entities.social import Story
from clean.use_cases.interfaces.repositories import StoryRepository


class CreateStoryUseCase:
    def __init__(self, story_repo: StoryRepository):
        self.story_repo = story_repo

    async def execute(self, author_id: int, image_url: str | None, content: str | None) -> dict:
        story = await self.story_repo.create(Story(author_id=author_id, image_url=image_url, content=content))
        return {
            "id": story.id, "author_id": story.author_id,
            "image_url": story.image_url, "content": story.content,
            "created_at": story.created_at,
        }
