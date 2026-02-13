from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession


@dataclass
class RegisterUser:
    username: str
    email: str
    password: str
    full_name: str | None
    db: AsyncSession


@dataclass
class LoginUser:
    email: str
    password: str
    db: AsyncSession


@dataclass
class UpdateUser:
    user_id: int
    full_name: str | None = None
    bio: str | None = None
    profile_image_url: str | None = None
    db: AsyncSession | None = None


@dataclass
class CreatePost:
    author_id: int
    content: str | None
    image_url: str | None
    db: AsyncSession | None = None


@dataclass
class DeletePost:
    post_id: int
    user_id: int
    db: AsyncSession | None = None


@dataclass
class ToggleLike:
    post_id: int
    user_id: int
    db: AsyncSession | None = None


@dataclass
class CreateComment:
    post_id: int
    author_id: int
    content: str
    db: AsyncSession | None = None


@dataclass
class DeleteComment:
    comment_id: int
    user_id: int
    db: AsyncSession | None = None


@dataclass
class FollowUser:
    follower_id: int
    following_id: int
    db: AsyncSession | None = None


@dataclass
class UnfollowUser:
    follower_id: int
    following_id: int
    db: AsyncSession | None = None


@dataclass
class CreateStory:
    author_id: int
    image_url: str | None
    content: str | None
    db: AsyncSession | None = None


@dataclass
class DeleteStory:
    story_id: int
    user_id: int
    db: AsyncSession | None = None


@dataclass
class SendMessage:
    sender_id: int
    receiver_id: int
    content: str
    db: AsyncSession | None = None


@dataclass
class MarkMessagesRead:
    user_id: int
    sender_id: int
    db: AsyncSession | None = None


@dataclass
class MarkNotificationRead:
    notification_id: int
    user_id: int
    db: AsyncSession | None = None


@dataclass
class MarkAllNotificationsRead:
    user_id: int
    db: AsyncSession | None = None
