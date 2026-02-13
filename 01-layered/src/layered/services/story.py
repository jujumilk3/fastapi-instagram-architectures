from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from layered.models.story import Story
from layered.repositories.follow import FollowRepository
from layered.repositories.story import StoryRepository
from layered.schemas.story import StoryCreate, StoryResponse


def _story_to_response(story: Story) -> StoryResponse:
    return StoryResponse(
        id=story.id,
        author_id=story.author_id,
        author_username=story.author.username if story.author else None,
        image_url=story.image_url,
        content=story.content,
        created_at=story.created_at,
    )


class StoryService:
    def __init__(self, db: AsyncSession):
        self.story_repo = StoryRepository(db)
        self.follow_repo = FollowRepository(db)

    async def create(self, author_id: int, data: StoryCreate) -> StoryResponse:
        story = Story(author_id=author_id, image_url=data.image_url, content=data.content)
        story = await self.story_repo.create(story)
        return StoryResponse(
            id=story.id,
            author_id=story.author_id,
            image_url=story.image_url,
            content=story.content,
            created_at=story.created_at,
        )

    async def get_my_stories(self, user_id: int) -> list[StoryResponse]:
        stories = await self.story_repo.get_active_by_author(user_id)
        return [_story_to_response(s) for s in stories]

    async def get_feed(self, user_id: int) -> list[StoryResponse]:
        following_ids = await self.follow_repo.get_following(user_id)
        following_ids.append(user_id)
        stories = await self.story_repo.get_feed(following_ids)
        return [_story_to_response(s) for s in stories]

    async def delete(self, story_id: int, user_id: int) -> None:
        story = await self.story_repo.get_by_id(story_id)
        if not story:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Story not found")
        if story.author_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your story")
        await self.story_repo.delete(story)
