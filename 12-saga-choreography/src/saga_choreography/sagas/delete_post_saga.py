from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from saga_choreography.models.tables import Comment, Like
from saga_choreography.services import hashtag_service, post_service
from saga_choreography.shared.saga import SagaStep


def build_steps(post_id: int, user_id: int, db: AsyncSession):
    async def action_delete_comments(ctx):
        result = await db.execute(select(Comment).where(Comment.post_id == post_id))
        for comment in result.scalars().all():
            await db.delete(comment)
        await db.flush()

    async def action_delete_likes(ctx):
        result = await db.execute(select(Like).where(Like.post_id == post_id))
        for like in result.scalars().all():
            await db.delete(like)
        await db.flush()

    async def action_delete_hashtags(ctx):
        await hashtag_service.delete_post_hashtags(post_id, db)

    async def action_delete_post(ctx):
        await post_service.delete_post(post_id=post_id, user_id=user_id, db=db)

    # Delete saga: no compensations - once we start deleting, we commit
    return [
        SagaStep(name="delete_comments", action=action_delete_comments),
        SagaStep(name="delete_likes", action=action_delete_likes),
        SagaStep(name="delete_hashtags", action=action_delete_hashtags),
        SagaStep(name="delete_post", action=action_delete_post),
    ]
