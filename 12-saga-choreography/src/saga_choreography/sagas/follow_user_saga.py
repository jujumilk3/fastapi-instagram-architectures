from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from saga_choreography.models.tables import User
from saga_choreography.services import follow_service, notification_service
from saga_choreography.shared.saga import SagaStep


def build_steps(follower_id: int, following_id: int, db: AsyncSession):
    async def action_create_follow(ctx):
        follow = await follow_service.create_follow(
            follower_id=follower_id, following_id=following_id, db=db
        )
        ctx["follow_id"] = follow.id
        return follow

    async def compensate_create_follow(ctx):
        await follow_service.delete_follow(
            follower_id=follower_id, following_id=following_id, db=db
        )

    async def action_create_notification(ctx):
        actor_result = await db.execute(select(User.username).where(User.id == follower_id))
        actor_username = actor_result.scalar_one_or_none() or "Someone"

        notif = await notification_service.create_notification(
            user_id=following_id,
            actor_id=follower_id,
            type="follow",
            reference_id=follower_id,
            message=f"{actor_username} started following you",
            db=db,
        )
        ctx["notification_id"] = notif.id

    async def compensate_notification(ctx):
        notif_id = ctx.get("notification_id")
        if notif_id:
            await notification_service.delete_notification_by_id(notif_id, db)

    return [
        SagaStep(
            name="create_follow",
            action=action_create_follow,
            compensation=compensate_create_follow,
        ),
        SagaStep(
            name="create_notification",
            action=action_create_notification,
            compensation=compensate_notification,
        ),
    ]
