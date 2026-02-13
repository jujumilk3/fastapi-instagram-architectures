from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from saga_choreography.models.tables import Post, User
from saga_choreography.services import comment_service, notification_service
from saga_choreography.shared.saga import SagaStep


def build_steps(post_id: int, author_id: int, content: str, db: AsyncSession):
    async def action_create_comment(ctx):
        comment = await comment_service.create_comment(
            post_id=post_id, author_id=author_id, content=content, db=db
        )
        ctx["comment_id"] = comment.id
        ctx["comment"] = comment
        return comment

    async def compensate_create_comment(ctx):
        comment_id = ctx.get("comment_id")
        if comment_id:
            await comment_service.delete_comment_by_id(comment_id, db)

    async def action_create_notification(ctx):
        post_result = await db.execute(select(Post).where(Post.id == post_id))
        post = post_result.scalar_one_or_none()
        if not post or post.author_id == author_id:
            return

        actor_result = await db.execute(select(User.username).where(User.id == author_id))
        actor_username = actor_result.scalar_one_or_none() or "Someone"

        notif = await notification_service.create_notification(
            user_id=post.author_id,
            actor_id=author_id,
            type="comment",
            reference_id=post_id,
            message=f"{actor_username} commented on your post",
            db=db,
        )
        ctx["notification_id"] = notif.id

    async def compensate_notification(ctx):
        notif_id = ctx.get("notification_id")
        if notif_id:
            await notification_service.delete_notification_by_id(notif_id, db)

    return [
        SagaStep(
            name="create_comment",
            action=action_create_comment,
            compensation=compensate_create_comment,
        ),
        SagaStep(
            name="create_notification",
            action=action_create_notification,
            compensation=compensate_notification,
        ),
    ]
