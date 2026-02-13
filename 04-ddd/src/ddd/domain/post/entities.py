from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from ddd.domain.shared.entity import Entity


@dataclass
class Comment(Entity):
    post_id: int = 0
    author_id: int = 0
    content: str = ""


@dataclass
class Like(Entity):
    post_id: int = 0
    user_id: int = 0
