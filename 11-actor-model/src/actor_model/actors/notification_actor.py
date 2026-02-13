from sqlalchemy import select, update

from actor_model.actors.base import Actor, Message
from actor_model.actors.messages import (
    GetNotificationsMessage,
    MarkAllNotificationsReadMessage,
    MarkNotificationReadMessage,
)
from actor_model.models.tables import Notification


class NotificationActor(Actor):
    async def receive(self, message: Message):
        match message:
            case GetNotificationsMessage():
                await self._handle_get(message)
            case MarkNotificationReadMessage():
                await self._handle_mark_read(message)
            case MarkAllNotificationsReadMessage():
                await self._handle_mark_all_read(message)

    async def _handle_get(self, msg: GetNotificationsMessage):
        async with msg.db_factory() as db:
            result = await db.execute(
                select(Notification)
                .where(Notification.user_id == msg.user_id)
                .order_by(Notification.created_at.desc())
                .limit(msg.limit)
                .offset(msg.offset)
            )
            notifications = [
                {
                    "id": n.id,
                    "user_id": n.user_id,
                    "actor_id": n.actor_id,
                    "type": n.type,
                    "reference_id": n.reference_id,
                    "message": n.message,
                    "is_read": n.is_read,
                    "created_at": n.created_at,
                }
                for n in result.scalars().all()
            ]
            msg.reply(notifications)

    async def _handle_mark_read(self, msg: MarkNotificationReadMessage):
        async with msg.db_factory() as db:
            await db.execute(
                update(Notification)
                .where(Notification.id == msg.notification_id, Notification.user_id == msg.user_id)
                .values(is_read=True)
            )
            await db.commit()
            msg.reply({"status": "ok"})

    async def _handle_mark_all_read(self, msg: MarkAllNotificationsReadMessage):
        async with msg.db_factory() as db:
            await db.execute(
                update(Notification)
                .where(Notification.user_id == msg.user_id, Notification.is_read.is_(False))
                .values(is_read=True)
            )
            await db.commit()
            msg.reply({"status": "ok"})
