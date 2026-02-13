from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from ddd.domain.shared.entity import Entity


@dataclass
class Notification(Entity):
    user_id: int = 0
    actor_id: int = 0
    type: str = ""
    reference_id: int | None = None
    message: str = ""
    is_read: bool = False
