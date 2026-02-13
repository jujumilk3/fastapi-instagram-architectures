from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from saga_choreography.models.tables import User
from saga_choreography.services import like_service, notification_service
from saga_choreography.shared.saga import SagaStep


def build_steps(post_id: int, user_id: int, db: AsyncSession):
    async def action_toggle_like(ctx):
        result = await like_service.toggle_like(post_id=post_id, user_id=user_id, db=db)
        ctx["like_result"] = result
        return result

    async def action_create_notification(ctx):
        result = ctx["like_result"]
        if not result.get("liked"):
            return

        post_author_id = result.get("post_author_id")
        if not post_author_id or post_author_id == user_id:
            return

        actor_result = await db.execute(select(User.username).where(User.id == user_id))
        actor_username = actor_result.scalar_one_or_none() or "Someone"

        notif = await notification_service.create_notification(
            user_id=post_author_id,
            actor_id=user_id,
            type="like",
            reference_id=post_id,
            message=f"{actor_username} liked your post",
            db=db,
        )
        ctx["notification_id"] = notif.id

    async def compensate_notification(ctx):
        notif_id = ctx.get("notification_id")
        if notif_id:
            await notification_service.delete_notification_by_id(notif_id, db)

    return [
        SagaStep(name="toggle_like", action=action_toggle_like),
        SagaStep(
            name="create_notification",
            action=action_create_notification,
            compensation=compensate_notification,
        ),
    ]
