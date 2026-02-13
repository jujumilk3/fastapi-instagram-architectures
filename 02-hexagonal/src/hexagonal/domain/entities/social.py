from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class Follow:
    id: int | None = None
    follower_id: int = 0
    following_id: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class Story:
    id: int | None = None
    author_id: int = 0
    image_url: str | None = None
    content: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class Message:
    id: int | None = None
    sender_id: int = 0
    receiver_id: int = 0
    content: str = ""
    is_read: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class Notification:
    id: int | None = None
    user_id: int = 0
    actor_id: int = 0
    type: str = ""
    reference_id: int | None = None
    message: str = ""
    is_read: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class Hashtag:
    id: int | None = None
    name: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
