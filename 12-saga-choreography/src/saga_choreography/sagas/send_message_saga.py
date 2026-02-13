from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from saga_choreography.models.tables import User
from saga_choreography.services import message_service, notification_service
from saga_choreography.shared.saga import SagaStep


def build_steps(sender_id: int, receiver_id: int, content: str, db: AsyncSession):
    async def action_create_message(ctx):
        msg = await message_service.create_message(
            sender_id=sender_id, receiver_id=receiver_id, content=content, db=db
        )
        ctx["message_id"] = msg.id
        ctx["message"] = msg
        return msg

    async def compensate_create_message(ctx):
        msg_id = ctx.get("message_id")
        if msg_id:
            await message_service.delete_message_by_id(msg_id, db)

    async def action_create_notification(ctx):
        actor_result = await db.execute(select(User.username).where(User.id == sender_id))
        actor_username = actor_result.scalar_one_or_none() or "Someone"

        notif = await notification_service.create_notification(
            user_id=receiver_id,
            actor_id=sender_id,
            type="message",
            reference_id=ctx["message_id"],
            message=f"{actor_username} sent you a message",
            db=db,
        )
        ctx["notification_id"] = notif.id

    async def compensate_notification(ctx):
        notif_id = ctx.get("notification_id")
        if notif_id:
            await notification_service.delete_notification_by_id(notif_id, db)

    return [
        SagaStep(
            name="create_message",
            action=action_create_message,
            compensation=compensate_create_message,
        ),
        SagaStep(
            name="create_notification",
            action=action_create_notification,
            compensation=compensate_notification,
        ),
    ]
