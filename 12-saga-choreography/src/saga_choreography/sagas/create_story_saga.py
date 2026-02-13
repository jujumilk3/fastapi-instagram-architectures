from sqlalchemy.ext.asyncio import AsyncSession

from saga_choreography.services import story_service
from saga_choreography.shared.saga import SagaStep


def build_steps(author_id: int, image_url: str | None, content: str | None, db: AsyncSession):
    async def action_create_story(ctx):
        story = await story_service.create_story(
            author_id=author_id, image_url=image_url, content=content, db=db
        )
        ctx["story_id"] = story.id
        ctx["story"] = story
        return story

    async def compensate_create_story(ctx):
        story_id = ctx.get("story_id")
        if story_id:
            await story_service.delete_story_by_id(story_id, db)

    return [
        SagaStep(
            name="create_story",
            action=action_create_story,
            compensation=compensate_create_story,
        ),
    ]
