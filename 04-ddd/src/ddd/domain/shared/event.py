from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass(frozen=True)
class DomainEvent:
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True)
class UserRegisteredEvent(DomainEvent):
    user_id: int = 0
    username: str = ""
    email: str = ""


@dataclass(frozen=True)
class ProfileUpdatedEvent(DomainEvent):
    user_id: int = 0


@dataclass(frozen=True)
class PostCreatedEvent(DomainEvent):
    post_id: int = 0
    author_id: int = 0


@dataclass(frozen=True)
class PostLikedEvent(DomainEvent):
    post_id: int = 0
    user_id: int = 0
    author_id: int = 0


@dataclass(frozen=True)
class PostUnlikedEvent(DomainEvent):
    post_id: int = 0
    user_id: int = 0


@dataclass(frozen=True)
class CommentAddedEvent(DomainEvent):
    comment_id: int = 0
    post_id: int = 0
    author_id: int = 0
    post_author_id: int = 0


@dataclass(frozen=True)
class UserFollowedEvent(DomainEvent):
    follower_id: int = 0
    following_id: int = 0


@dataclass(frozen=True)
class UserUnfollowedEvent(DomainEvent):
    follower_id: int = 0
    following_id: int = 0
