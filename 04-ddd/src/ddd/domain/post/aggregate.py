from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone

from ddd.domain.post.entities import Comment, Like
from ddd.domain.shared.event import (
    CommentAddedEvent,
    PostCreatedEvent,
    PostLikedEvent,
    PostUnlikedEvent,
)


@dataclass
class PostAggregate:
    id: int | None = None
    author_id: int = 0
    content: str | None = None
    image_url: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime | None = None
    _events: list = field(default_factory=list, repr=False, compare=False)

    @classmethod
    def create(
        cls,
        author_id: int,
        content: str | None = None,
        image_url: str | None = None,
    ) -> PostAggregate:
        post = cls(author_id=author_id, content=content, image_url=image_url)
        post._events.append(PostCreatedEvent(post_id=0, author_id=author_id))
        return post

    @classmethod
    def reconstitute(
        cls,
        id: int,
        author_id: int,
        content: str | None,
        image_url: str | None,
        created_at: datetime,
        updated_at: datetime | None,
    ) -> PostAggregate:
        return cls(
            id=id,
            author_id=author_id,
            content=content,
            image_url=image_url,
            created_at=created_at,
            updated_at=updated_at,
        )

    def extract_hashtags(self) -> list[str]:
        if not self.content:
            return []
        return [tag.lower() for tag in re.findall(r"#(\w+)", self.content)]

    def add_comment(
        self, author_id: int, content: str, comment_id: int = 0
    ) -> Comment:
        comment = Comment(
            id=comment_id, post_id=self.id, author_id=author_id, content=content
        )
        if self.author_id != author_id:
            self._events.append(CommentAddedEvent(
                comment_id=comment_id,
                post_id=self.id,
                author_id=author_id,
                post_author_id=self.author_id,
            ))
        return comment

    def toggle_like(
        self, user_id: int, already_liked: bool
    ) -> bool:
        if already_liked:
            self._events.append(PostUnlikedEvent(post_id=self.id, user_id=user_id))
            return False
        self._events.append(PostLikedEvent(
            post_id=self.id, user_id=user_id, author_id=self.author_id,
        ))
        return True

    def collect_events(self) -> list:
        events = self._events.copy()
        self._events.clear()
        return events
