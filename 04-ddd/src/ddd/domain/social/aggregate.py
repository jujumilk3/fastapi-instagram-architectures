from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from ddd.domain.shared.entity import Entity


@dataclass
class Follow(Entity):
    follower_id: int = 0
    following_id: int = 0


@dataclass
class Story(Entity):
    author_id: int = 0
    image_url: str | None = None
    content: str | None = None
