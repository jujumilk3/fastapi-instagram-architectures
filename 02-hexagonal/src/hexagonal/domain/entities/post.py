from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class Post:
    id: int | None = None
    author_id: int = 0
    content: str | None = None
    image_url: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime | None = None


@dataclass
class Comment:
    id: int | None = None
    post_id: int = 0
    author_id: int = 0
    content: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class Like:
    id: int | None = None
    post_id: int = 0
    user_id: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
