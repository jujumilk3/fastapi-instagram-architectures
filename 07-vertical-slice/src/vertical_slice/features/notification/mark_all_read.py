from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from vertical_slice.models.tables import Notification


@dataclass
class MarkAllReadRequest:
    user_id: int
    db: AsyncSession


async def mark_all_read_handler(request: MarkAllReadRequest) -> dict:
    db = request.db
    await db.execute(
        update(Notification)
        .where(Notification.user_id == request.user_id, Notification.is_read.is_(False))
        .values(is_read=True)
    )
    await db.flush()
    return {"status": "ok"}
