from contextlib import asynccontextmanager

from fastapi import FastAPI

from cqrs_es.api.routers import (
    auth_router,
    feed_router,
    follow_router,
    message_router,
    notification_router,
    post_router,
    search_router,
    story_router,
    user_router,
)
from cqrs_es.read.handlers.handlers import (
    handle_get_conversation,
    handle_get_conversations,
    handle_get_feed,
    handle_get_my_stories,
    handle_get_notifications,
    handle_get_post,
    handle_get_post_comments,
    handle_get_posts_by_hashtag,
    handle_get_story_feed,
    handle_get_user_by_email,
    handle_get_user_by_id,
    handle_get_user_followers,
    handle_get_user_following,
    handle_get_user_posts,
    handle_get_user_profile,
    handle_search_hashtags,
    handle_search_users,
)
from cqrs_es.read.projections.handlers import (
    on_all_notifications_read,
    on_comment_created,
    on_comment_deleted,
    on_like_added,
    on_like_removed,
    on_message_sent,
    on_messages_marked_read,
    on_notification_read,
    on_post_created,
    on_post_deleted,
    on_story_created,
    on_story_deleted,
    on_user_followed,
    on_user_registered,
    on_user_unfollowed,
    on_user_updated,
)
from cqrs_es.read.projections.models import *  # noqa: F403
from cqrs_es.read.queries.queries import (
    GetConversation,
    GetConversations,
    GetFeed,
    GetMyStories,
    GetNotifications,
    GetPost,
    GetPostComments,
    GetPostsByHashtag,
    GetStoryFeed,
    GetUserByEmail,
    GetUserById,
    GetUserFollowers,
    GetUserFollowing,
    GetUserPosts,
    GetUserProfile,
    SearchHashtags,
    SearchUsers,
)
from cqrs_es.shared import command_bus, event_bus, query_bus
from cqrs_es.shared.database import Base, engine
from cqrs_es.shared.event_store import EventStoreModel  # noqa: F401
from cqrs_es.write.commands.commands import (
    CreateComment,
    CreatePost,
    CreateStory,
    DeleteComment,
    DeletePost,
    DeleteStory,
    FollowUser,
    LoginUser,
    MarkAllNotificationsRead,
    MarkMessagesRead,
    MarkNotificationRead,
    RegisterUser,
    SendMessage,
    ToggleLike,
    UnfollowUser,
    UpdateUser,
)
from cqrs_es.write.events.events import (
    ALL_NOTIFICATIONS_READ,
    COMMENT_CREATED,
    COMMENT_DELETED,
    LIKE_ADDED,
    LIKE_REMOVED,
    MESSAGE_SENT,
    MESSAGES_MARKED_READ,
    NOTIFICATION_READ,
    POST_CREATED,
    POST_DELETED,
    STORY_CREATED,
    STORY_DELETED,
    USER_FOLLOWED,
    USER_REGISTERED,
    USER_UNFOLLOWED,
    USER_UPDATED,
)
from cqrs_es.write.handlers.auth import (
    handle_login_user,
    handle_register_user,
    handle_update_user,
)
from cqrs_es.write.handlers.messaging import (
    handle_mark_all_notifications_read,
    handle_mark_messages_read,
    handle_mark_notification_read,
    handle_send_message,
)
from cqrs_es.write.handlers.post import (
    handle_create_comment,
    handle_create_post,
    handle_delete_comment,
    handle_delete_post,
    handle_toggle_like,
)
from cqrs_es.write.handlers.social import (
    handle_create_story,
    handle_delete_story,
    handle_follow_user,
    handle_unfollow_user,
)


def _register_command_handlers() -> None:
    command_bus.clear_handlers()
    command_bus.register_command_handler(RegisterUser, handle_register_user)
    command_bus.register_command_handler(LoginUser, handle_login_user)
    command_bus.register_command_handler(UpdateUser, handle_update_user)
    command_bus.register_command_handler(CreatePost, handle_create_post)
    command_bus.register_command_handler(DeletePost, handle_delete_post)
    command_bus.register_command_handler(ToggleLike, handle_toggle_like)
    command_bus.register_command_handler(CreateComment, handle_create_comment)
    command_bus.register_command_handler(DeleteComment, handle_delete_comment)
    command_bus.register_command_handler(FollowUser, handle_follow_user)
    command_bus.register_command_handler(UnfollowUser, handle_unfollow_user)
    command_bus.register_command_handler(CreateStory, handle_create_story)
    command_bus.register_command_handler(DeleteStory, handle_delete_story)
    command_bus.register_command_handler(SendMessage, handle_send_message)
    command_bus.register_command_handler(MarkMessagesRead, handle_mark_messages_read)
    command_bus.register_command_handler(MarkNotificationRead, handle_mark_notification_read)
    command_bus.register_command_handler(MarkAllNotificationsRead, handle_mark_all_notifications_read)


def _register_query_handlers() -> None:
    query_bus.clear_handlers()
    query_bus.register_query_handler(GetUserById, handle_get_user_by_id)
    query_bus.register_query_handler(GetUserByEmail, handle_get_user_by_email)
    query_bus.register_query_handler(GetUserProfile, handle_get_user_profile)
    query_bus.register_query_handler(GetUserPosts, handle_get_user_posts)
    query_bus.register_query_handler(GetUserFollowers, handle_get_user_followers)
    query_bus.register_query_handler(GetUserFollowing, handle_get_user_following)
    query_bus.register_query_handler(GetPost, handle_get_post)
    query_bus.register_query_handler(GetPostComments, handle_get_post_comments)
    query_bus.register_query_handler(GetFeed, handle_get_feed)
    query_bus.register_query_handler(GetMyStories, handle_get_my_stories)
    query_bus.register_query_handler(GetStoryFeed, handle_get_story_feed)
    query_bus.register_query_handler(GetConversations, handle_get_conversations)
    query_bus.register_query_handler(GetConversation, handle_get_conversation)
    query_bus.register_query_handler(GetNotifications, handle_get_notifications)
    query_bus.register_query_handler(SearchUsers, handle_search_users)
    query_bus.register_query_handler(SearchHashtags, handle_search_hashtags)
    query_bus.register_query_handler(GetPostsByHashtag, handle_get_posts_by_hashtag)


def _register_event_subscribers() -> None:
    event_bus.clear_subscribers()
    event_bus.subscribe(USER_REGISTERED, on_user_registered)
    event_bus.subscribe(USER_UPDATED, on_user_updated)
    event_bus.subscribe(POST_CREATED, on_post_created)
    event_bus.subscribe(POST_DELETED, on_post_deleted)
    event_bus.subscribe(LIKE_ADDED, on_like_added)
    event_bus.subscribe(LIKE_REMOVED, on_like_removed)
    event_bus.subscribe(COMMENT_CREATED, on_comment_created)
    event_bus.subscribe(COMMENT_DELETED, on_comment_deleted)
    event_bus.subscribe(USER_FOLLOWED, on_user_followed)
    event_bus.subscribe(USER_UNFOLLOWED, on_user_unfollowed)
    event_bus.subscribe(STORY_CREATED, on_story_created)
    event_bus.subscribe(STORY_DELETED, on_story_deleted)
    event_bus.subscribe(MESSAGE_SENT, on_message_sent)
    event_bus.subscribe(MESSAGES_MARKED_READ, on_messages_marked_read)
    event_bus.subscribe(NOTIFICATION_READ, on_notification_read)
    event_bus.subscribe(ALL_NOTIFICATIONS_READ, on_all_notifications_read)


@asynccontextmanager
async def lifespan(app: FastAPI):
    _register_command_handlers()
    _register_query_handlers()
    _register_event_subscribers()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(
    title="Instagram Clone - CQRS + Event Sourcing Architecture",
    lifespan=lifespan,
)

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(post_router)
app.include_router(follow_router)
app.include_router(feed_router)
app.include_router(story_router)
app.include_router(message_router)
app.include_router(notification_router)
app.include_router(search_router)
