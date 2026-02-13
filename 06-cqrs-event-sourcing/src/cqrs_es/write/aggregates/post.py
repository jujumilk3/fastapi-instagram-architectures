from datetime import datetime, timezone

from cqrs_es.write.events.events import (
    COMMENT_CREATED,
    COMMENT_DELETED,
    LIKE_ADDED,
    LIKE_REMOVED,
    POST_CREATED,
    POST_DELETED,
)


class PostAggregate:
    def __init__(self) -> None:
        self.id: int | None = None
        self.author_id: int | None = None
        self.content: str | None = None
        self.image_url: str | None = None
        self.deleted: bool = False
        self.likes: set[int] = set()
        self.comments: dict[int, dict] = {}
        self.version: int = 0

    def apply(self, event_type: str, data: dict) -> None:
        if event_type == POST_CREATED:
            self.id = data["post_id"]
            self.author_id = data["author_id"]
            self.content = data.get("content")
            self.image_url = data.get("image_url")
        elif event_type == POST_DELETED:
            self.deleted = True
        elif event_type == LIKE_ADDED:
            self.likes.add(data["user_id"])
        elif event_type == LIKE_REMOVED:
            self.likes.discard(data["user_id"])
        elif event_type == COMMENT_CREATED:
            self.comments[data["comment_id"]] = data
        elif event_type == COMMENT_DELETED:
            self.comments.pop(data["comment_id"], None)
        self.version += 1

    @staticmethod
    def create(post_id: int, author_id: int, content: str | None,
               image_url: str | None) -> tuple[str, dict]:
        return POST_CREATED, {
            "post_id": post_id,
            "author_id": author_id,
            "content": content,
            "image_url": image_url,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

    @staticmethod
    def delete(post_id: int, author_id: int) -> tuple[str, dict]:
        return POST_DELETED, {"post_id": post_id, "author_id": author_id}

    @staticmethod
    def add_like(post_id: int, user_id: int, post_author_id: int) -> tuple[str, dict]:
        return LIKE_ADDED, {
            "post_id": post_id,
            "user_id": user_id,
            "post_author_id": post_author_id,
        }

    @staticmethod
    def remove_like(post_id: int, user_id: int) -> tuple[str, dict]:
        return LIKE_REMOVED, {"post_id": post_id, "user_id": user_id}

    @staticmethod
    def add_comment(comment_id: int, post_id: int, author_id: int,
                    content: str, post_author_id: int) -> tuple[str, dict]:
        return COMMENT_CREATED, {
            "comment_id": comment_id,
            "post_id": post_id,
            "author_id": author_id,
            "content": content,
            "post_author_id": post_author_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

    @staticmethod
    def remove_comment(comment_id: int, post_id: int) -> tuple[str, dict]:
        return COMMENT_DELETED, {"comment_id": comment_id, "post_id": post_id}
