import json
from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, String, Text, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from cqrs_es.shared.database import Base


class EventStoreModel(Base):
    __tablename__ = "event_store"

    id: Mapped[int] = mapped_column(primary_key=True)
    aggregate_type: Mapped[str] = mapped_column(String(100))
    aggregate_id: Mapped[str] = mapped_column(String(100), index=True)
    event_type: Mapped[str] = mapped_column(String(100))
    event_data: Mapped[str] = mapped_column(Text)
    version: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


async def append_event(
    db: AsyncSession,
    aggregate_type: str,
    aggregate_id: str,
    event_type: str,
    event_data: dict,
    version: int,
) -> EventStoreModel:
    entry = EventStoreModel(
        aggregate_type=aggregate_type,
        aggregate_id=aggregate_id,
        event_type=event_type,
        event_data=json.dumps(event_data),
        version=version,
        created_at=datetime.now(timezone.utc),
    )
    db.add(entry)
    await db.flush()
    return entry


async def load_events(
    db: AsyncSession, aggregate_type: str, aggregate_id: str
) -> list[dict]:
    stmt = (
        select(EventStoreModel)
        .where(
            EventStoreModel.aggregate_type == aggregate_type,
            EventStoreModel.aggregate_id == aggregate_id,
        )
        .order_by(EventStoreModel.version)
    )
    result = await db.execute(stmt)
    rows = result.scalars().all()
    return [
        {
            "event_type": row.event_type,
            "event_data": json.loads(row.event_data),
            "version": row.version,
            "created_at": row.created_at,
        }
        for row in rows
    ]


async def get_next_version(
    db: AsyncSession, aggregate_type: str, aggregate_id: str
) -> int:
    events = await load_events(db, aggregate_type, aggregate_id)
    if not events:
        return 1
    return events[-1]["version"] + 1
