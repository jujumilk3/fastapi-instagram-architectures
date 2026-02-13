from datetime import datetime, timezone

from cqrs_es.write.events.events import (
    ALL_NOTIFICATIONS_READ,
    MESSAGE_SENT,
    MESSAGES_MARKED_READ,
    NOTIFICATION_READ,
    STORY_CREATED,
    STORY_DELETED,
    USER_FOLLOWED,
    USER_UNFOLLOWED,
)


class FollowAggregate:
    def __init__(self) -> None:
        self.following: set[int] = set()
        self.version: int = 0

    def apply(self, event_type: str, data: dict) -> None:
        if event_type == USER_FOLLOWED:
            self.following.add(data["following_id"])
        elif event_type == USER_UNFOLLOWED:
            self.following.discard(data["following_id"])
        self.version += 1

    @staticmethod
    def follow(follower_id: int, following_id: int) -> tuple[str, dict]:
        return USER_FOLLOWED, {
            "follower_id": follower_id,
            "following_id": following_id,
        }

    @staticmethod
    def unfollow(follower_id: int, following_id: int) -> tuple[str, dict]:
        return USER_UNFOLLOWED, {
            "follower_id": follower_id,
            "following_id": following_id,
        }


class StoryAggregate:
    @staticmethod
    def create(story_id: int, author_id: int, image_url: str | None,
               content: str | None) -> tuple[str, dict]:
        return STORY_CREATED, {
            "story_id": story_id,
            "author_id": author_id,
            "image_url": image_url,
            "content": content,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

    @staticmethod
    def delete(story_id: int, author_id: int) -> tuple[str, dict]:
        return STORY_DELETED, {
            "story_id": story_id,
            "author_id": author_id,
        }


class MessageAggregate:
    @staticmethod
    def send(message_id: int, sender_id: int, receiver_id: int,
             content: str) -> tuple[str, dict]:
        return MESSAGE_SENT, {
            "message_id": message_id,
            "sender_id": sender_id,
            "receiver_id": receiver_id,
            "content": content,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

    @staticmethod
    def mark_read(user_id: int, sender_id: int) -> tuple[str, dict]:
        return MESSAGES_MARKED_READ, {
            "user_id": user_id,
            "sender_id": sender_id,
        }


class NotificationAggregate:
    @staticmethod
    def mark_read(notification_id: int, user_id: int) -> tuple[str, dict]:
        return NOTIFICATION_READ, {
            "notification_id": notification_id,
            "user_id": user_id,
        }

    @staticmethod
    def mark_all_read(user_id: int) -> tuple[str, dict]:
        return ALL_NOTIFICATIONS_READ, {"user_id": user_id}
