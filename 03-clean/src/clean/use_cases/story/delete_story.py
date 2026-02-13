from fastapi import HTTPException, status

from clean.use_cases.interfaces.repositories import StoryRepository


class DeleteStoryUseCase:
    def __init__(self, story_repo: StoryRepository):
        self.story_repo = story_repo

    async def execute(self, story_id: int, user_id: int) -> None:
        story = await self.story_repo.get_by_id(story_id)
        if not story:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Story not found")
        if story.author_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your story")
        await self.story_repo.delete(story_id)
