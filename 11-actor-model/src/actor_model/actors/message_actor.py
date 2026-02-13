from sqlalchemy import and_, case, func, or_, select

from actor_model.actors.base import Actor, Message
from actor_model.actors.messages import (
    GetConversationMessage,
    GetConversationsMessage,
    MarkMessagesReadMessage,
    SendDirectMessage,
)
from actor_model.models.tables import Message as DBMessage
from actor_model.models.tables import User


class MessageActor(Actor):
    async def receive(self, message: Message):
        match message:
            case SendDirectMessage():
                await self._handle_send(message)
            case GetConversationsMessage():
                await self._handle_get_conversations(message)
            case GetConversationMessage():
                await self._handle_get_conversation(message)
            case MarkMessagesReadMessage():
                await self._handle_mark_read(message)

    async def _handle_send(self, msg: SendDirectMessage):
        async with msg.db_factory() as db:
            receiver = await db.get(User, msg.receiver_id)
            if not receiver:
                raise ValueError("Receiver not found")

            dm = DBMessage(sender_id=msg.sender_id, receiver_id=msg.receiver_id, content=msg.content)
            db.add(dm)
            await db.flush()
            await db.refresh(dm)

            result = {
                "id": dm.id,
                "sender_id": dm.sender_id,
                "receiver_id": dm.receiver_id,
                "content": dm.content,
                "is_read": dm.is_read,
                "created_at": dm.created_at,
            }
            await db.commit()
            msg.reply(result)

    async def _handle_get_conversations(self, msg: GetConversationsMessage):
        async with msg.db_factory() as db:
            other_user = case(
                (DBMessage.sender_id == msg.user_id, DBMessage.receiver_id),
                else_=DBMessage.sender_id,
            )
            subq = (
                select(
                    other_user.label("other_user_id"),
                    func.max(DBMessage.id).label("last_message_id"),
                )
                .where(or_(DBMessage.sender_id == msg.user_id, DBMessage.receiver_id == msg.user_id))
                .group_by(other_user)
                .subquery()
            )
            result = await db.execute(
                select(DBMessage)
                .join(subq, DBMessage.id == subq.c.last_message_id)
                .order_by(DBMessage.created_at.desc())
            )
            convos = []
            for m in result.scalars().all():
                other_id = m.receiver_id if m.sender_id == msg.user_id else m.sender_id
                convos.append({
                    "other_user_id": other_id,
                    "last_message": {
                        "id": m.id,
                        "sender_id": m.sender_id,
                        "receiver_id": m.receiver_id,
                        "content": m.content,
                        "is_read": m.is_read,
                        "created_at": m.created_at,
                    },
                })
            msg.reply(convos)

    async def _handle_get_conversation(self, msg: GetConversationMessage):
        async with msg.db_factory() as db:
            result = await db.execute(
                select(DBMessage)
                .where(
                    or_(
                        and_(DBMessage.sender_id == msg.user_id, DBMessage.receiver_id == msg.other_user_id),
                        and_(DBMessage.sender_id == msg.other_user_id, DBMessage.receiver_id == msg.user_id),
                    )
                )
                .order_by(DBMessage.created_at.desc())
                .limit(msg.limit)
                .offset(msg.offset)
            )
            messages = [
                {
                    "id": m.id,
                    "sender_id": m.sender_id,
                    "receiver_id": m.receiver_id,
                    "content": m.content,
                    "is_read": m.is_read,
                    "created_at": m.created_at,
                }
                for m in result.scalars().all()
            ]
            msg.reply(messages)

    async def _handle_mark_read(self, msg: MarkMessagesReadMessage):
        async with msg.db_factory() as db:
            result = await db.execute(
                select(DBMessage).where(
                    DBMessage.sender_id == msg.sender_id,
                    DBMessage.receiver_id == msg.user_id,
                    DBMessage.is_read.is_(False),
                )
            )
            for dm in result.scalars().all():
                dm.is_read = True
            await db.commit()
            msg.reply({"status": "ok"})
