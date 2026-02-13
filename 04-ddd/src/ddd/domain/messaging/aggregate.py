from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from ddd.domain.shared.entity import Entity


@dataclass
class Message(Entity):
    sender_id: int = 0
    receiver_id: int = 0
    content: str = ""
    is_read: bool = False
