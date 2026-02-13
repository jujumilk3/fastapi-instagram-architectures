from dataclasses import dataclass, field

from sqlalchemy.ext.asyncio import async_sessionmaker

from actor_model.actors.base import Ask


# --- User ---

@dataclass
class RegisterMessage(Ask):
    username: str = ""
    email: str = ""
    password: str = ""
    full_name: str | None = None
    db_factory: async_sessionmaker | None = None


@dataclass
class LoginMessage(Ask):
    email: str = ""
    password: str = ""
    db_factory: async_sessionmaker | None = None


@dataclass
class GetProfileMessage(Ask):
    user_id: int = 0
    db_factory: async_sessionmaker | None = None


@dataclass
class GetCurrentUserMessage(Ask):
    user_id: int = 0
    db_factory: async_sessionmaker | None = None


@dataclass
class UpdateProfileMessage(Ask):
    user_id: int = 0
    update_data: dict = field(default_factory=dict)
    db_factory: async_sessionmaker | None = None


@dataclass
class GetFollowersMessage(Ask):
    user_id: int = 0
    db_factory: async_sessionmaker | None = None


@dataclass
class GetFollowingMessage(Ask):
    user_id: int = 0
    db_factory: async_sessionmaker | None = None


# --- Post ---

@dataclass
class CreatePostMessage(Ask):
    author_id: int = 0
    content: str | None = None
    image_url: str | None = None
    db_factory: async_sessionmaker | None = None


@dataclass
class GetPostMessage(Ask):
    post_id: int = 0
    db_factory: async_sessionmaker | None = None


@dataclass
class DeletePostMessage(Ask):
    post_id: int = 0
    user_id: int = 0
    db_factory: async_sessionmaker | None = None


@dataclass
class GetUserPostsMessage(Ask):
    user_id: int = 0
    limit: int = 20
    offset: int = 0
    db_factory: async_sessionmaker | None = None


# --- Comment ---

@dataclass
class CreateCommentMessage(Ask):
    post_id: int = 0
    author_id: int = 0
    content: str = ""
    db_factory: async_sessionmaker | None = None


@dataclass
class GetCommentsMessage(Ask):
    post_id: int = 0
    limit: int = 50
    offset: int = 0
    db_factory: async_sessionmaker | None = None


@dataclass
class DeleteCommentMessage(Ask):
    comment_id: int = 0
    user_id: int = 0
    db_factory: async_sessionmaker | None = None


# --- Like ---

@dataclass
class ToggleLikeMessage(Ask):
    post_id: int = 0
    user_id: int = 0
    db_factory: async_sessionmaker | None = None


# --- Follow ---

@dataclass
class FollowUserMessage(Ask):
    follower_id: int = 0
    following_id: int = 0
    db_factory: async_sessionmaker | None = None


@dataclass
class UnfollowUserMessage(Ask):
    follower_id: int = 0
    following_id: int = 0
    db_factory: async_sessionmaker | None = None


# --- Feed ---

@dataclass
class GetFeedMessage(Ask):
    user_id: int = 0
    limit: int = 20
    offset: int = 0
    db_factory: async_sessionmaker | None = None


# --- Story ---

@dataclass
class CreateStoryMessage(Ask):
    author_id: int = 0
    image_url: str | None = None
    content: str | None = None
    db_factory: async_sessionmaker | None = None


@dataclass
class GetStoriesMessage(Ask):
    user_id: int = 0
    db_factory: async_sessionmaker | None = None


@dataclass
class GetStoryFeedMessage(Ask):
    user_id: int = 0
    db_factory: async_sessionmaker | None = None


@dataclass
class DeleteStoryMessage(Ask):
    story_id: int = 0
    user_id: int = 0
    db_factory: async_sessionmaker | None = None


# --- Message (DM) ---

@dataclass
class SendDirectMessage(Ask):
    sender_id: int = 0
    receiver_id: int = 0
    content: str = ""
    db_factory: async_sessionmaker | None = None


@dataclass
class GetConversationsMessage(Ask):
    user_id: int = 0
    db_factory: async_sessionmaker | None = None


@dataclass
class GetConversationMessage(Ask):
    user_id: int = 0
    other_user_id: int = 0
    limit: int = 50
    offset: int = 0
    db_factory: async_sessionmaker | None = None


@dataclass
class MarkMessagesReadMessage(Ask):
    user_id: int = 0
    sender_id: int = 0
    db_factory: async_sessionmaker | None = None


# --- Notification ---

@dataclass
class CreateNotificationMessage(Ask):
    type: str = ""
    actor_id: int = 0
    target_user_id: int = 0
    reference_id: int | None = None
    db_factory: async_sessionmaker | None = None


@dataclass
class GetNotificationsMessage(Ask):
    user_id: int = 0
    limit: int = 50
    offset: int = 0
    db_factory: async_sessionmaker | None = None


@dataclass
class MarkNotificationReadMessage(Ask):
    notification_id: int = 0
    user_id: int = 0
    db_factory: async_sessionmaker | None = None


@dataclass
class MarkAllNotificationsReadMessage(Ask):
    user_id: int = 0
    db_factory: async_sessionmaker | None = None


# --- Search ---

@dataclass
class SearchUsersMessage(Ask):
    query: str = ""
    limit: int = 20
    db_factory: async_sessionmaker | None = None


@dataclass
class SearchHashtagsMessage(Ask):
    query: str = ""
    limit: int = 20
    db_factory: async_sessionmaker | None = None


@dataclass
class GetPostsByHashtagMessage(Ask):
    tag: str = ""
    limit: int = 20
    offset: int = 0
    db_factory: async_sessionmaker | None = None
