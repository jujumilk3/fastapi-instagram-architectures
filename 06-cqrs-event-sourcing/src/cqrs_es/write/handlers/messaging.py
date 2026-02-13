from fastapi import HTTPException, status
from sqlalchemy import select

from cqrs_es.read.projections.models import (
    MessageProjection,
    NotificationProjection,
    UserProjection,
)
from cqrs_es.shared import event_bus
from cqrs_es.shared.event_store import append_event, get_next_version
from cqrs_es.write.aggregates.social import MessageAggregate, NotificationAggregate
from cqrs_es.write.commands.commands import (
    MarkAllNotificationsRead,
    MarkMessagesRead,
    MarkNotificationRead,
    SendMessage,
)


async def handle_send_message(cmd: SendMessage) -> dict:
    result = await cmd.db.execute(
        select(UserProjection).where(UserProjection.id == cmd.receiver_id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Receiver not found")

    msg_result = await cmd.db.execute(
        select(MessageProjection.id).order_by(MessageProjection.id.desc()).limit(1)
    )
    max_id = msg_result.scalar_one_or_none() or 0
    message_id = max_id + 1

    event_type, event_data = MessageAggregate.send(
        message_id, cmd.sender_id, cmd.receiver_id, cmd.content
    )
    version = await get_next_version(cmd.db, "Message", str(message_id))
    await append_event(cmd.db, "Message", str(message_id), event_type, event_data, version)
    await event_bus.publish(event_type, event_data, db=cmd.db)

    result = await cmd.db.execute(
        select(MessageProjection).where(MessageProjection.id == message_id)
    )
    msg = result.scalar_one()
    return {
        "id": msg.id, "sender_id": msg.sender_id,
        "receiver_id": msg.receiver_id, "content": msg.content,
        "is_read": msg.is_read, "created_at": msg.created_at,
    }


async def handle_mark_messages_read(cmd: MarkMessagesRead) -> dict:
    event_type, event_data = MessageAggregate.mark_read(cmd.user_id, cmd.sender_id)
    aggregate_id = f"{cmd.user_id}-{cmd.sender_id}"
    version = await get_next_version(cmd.db, "MessageRead", aggregate_id)
    await append_event(cmd.db, "MessageRead", aggregate_id, event_type, event_data, version)
    await event_bus.publish(event_type, event_data, db=cmd.db)
    return {"status": "ok"}


async def handle_mark_notification_read(cmd: MarkNotificationRead) -> dict:
    event_type, event_data = NotificationAggregate.mark_read(cmd.notification_id, cmd.user_id)
    aggregate_id = f"notif-{cmd.notification_id}"
    version = await get_next_version(cmd.db, "Notification", aggregate_id)
    await append_event(cmd.db, "Notification", aggregate_id, event_type, event_data, version)
    await event_bus.publish(event_type, event_data, db=cmd.db)
    return {"status": "ok"}


async def handle_mark_all_notifications_read(cmd: MarkAllNotificationsRead) -> dict:
    event_type, event_data = NotificationAggregate.mark_all_read(cmd.user_id)
    aggregate_id = f"notif-user-{cmd.user_id}"
    version = await get_next_version(cmd.db, "Notification", aggregate_id)
    await append_event(cmd.db, "Notification", aggregate_id, event_type, event_data, version)
    await event_bus.publish(event_type, event_data, db=cmd.db)
    return {"status": "ok"}
