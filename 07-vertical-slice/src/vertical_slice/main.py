from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from vertical_slice.api.routers import (
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
from vertical_slice.models.base import Base
from vertical_slice.models.tables import (  # noqa: F401
    Comment,
    Follow,
    Hashtag,
    Like,
    Message,
    Notification,
    Post,
    PostHashtag,
    Story,
    User,
)
from vertical_slice.shared.database import engine
from vertical_slice.shared.mediator import mediator

from vertical_slice.features.auth.register import RegisterRequest, register_handler
from vertical_slice.features.auth.login import LoginRequest, login_handler
from vertical_slice.features.auth.get_me import GetMeRequest, get_me_handler
from vertical_slice.features.user.get_profile import GetProfileRequest, get_profile_handler
from vertical_slice.features.user.update_profile import UpdateProfileRequest, update_profile_handler
from vertical_slice.features.user.get_user_posts import GetUserPostsRequest, get_user_posts_handler
from vertical_slice.features.user.get_followers import GetFollowersRequest, get_followers_handler
from vertical_slice.features.user.get_following import GetFollowingRequest, get_following_handler
from vertical_slice.features.post.create_post import CreatePostRequest, create_post_handler
from vertical_slice.features.post.get_post import GetPostRequest, get_post_handler
from vertical_slice.features.post.delete_post import DeletePostRequest, delete_post_handler
from vertical_slice.features.comment.create_comment import CreateCommentRequest, create_comment_handler
from vertical_slice.features.comment.get_comments import GetCommentsRequest, get_comments_handler
from vertical_slice.features.comment.delete_comment import DeleteCommentRequest, delete_comment_handler
from vertical_slice.features.like.toggle_like import ToggleLikeRequest, toggle_like_handler
from vertical_slice.features.follow.follow_user import FollowUserRequest, follow_user_handler
from vertical_slice.features.follow.unfollow_user import UnfollowUserRequest, unfollow_user_handler
from vertical_slice.features.feed.get_feed import GetFeedRequest, get_feed_handler
from vertical_slice.features.story.create_story import CreateStoryRequest, create_story_handler
from vertical_slice.features.story.get_my_stories import GetMyStoriesRequest, get_my_stories_handler
from vertical_slice.features.story.get_story_feed import GetStoryFeedRequest, get_story_feed_handler
from vertical_slice.features.story.delete_story import DeleteStoryRequest, delete_story_handler
from vertical_slice.features.message.send_message import SendMessageRequest, send_message_handler
from vertical_slice.features.message.get_conversations import GetConversationsRequest, get_conversations_handler
from vertical_slice.features.message.get_conversation import GetConversationRequest, get_conversation_handler
from vertical_slice.features.message.mark_messages_read import MarkMessagesReadRequest, mark_messages_read_handler
from vertical_slice.features.notification.get_notifications import GetNotificationsRequest, get_notifications_handler
from vertical_slice.features.notification.mark_notification_read import MarkNotificationReadRequest, mark_notification_read_handler
from vertical_slice.features.notification.mark_all_read import MarkAllReadRequest, mark_all_read_handler
from vertical_slice.features.search.search_users import SearchUsersRequest, search_users_handler
from vertical_slice.features.search.search_hashtags import SearchHashtagsRequest, search_hashtags_handler
from vertical_slice.features.search.get_posts_by_hashtag import GetPostsByHashtagRequest, get_posts_by_hashtag_handler


def _register_handlers() -> None:
    mediator.register(RegisterRequest, register_handler)
    mediator.register(LoginRequest, login_handler)
    mediator.register(GetMeRequest, get_me_handler)
    mediator.register(GetProfileRequest, get_profile_handler)
    mediator.register(UpdateProfileRequest, update_profile_handler)
    mediator.register(GetUserPostsRequest, get_user_posts_handler)
    mediator.register(GetFollowersRequest, get_followers_handler)
    mediator.register(GetFollowingRequest, get_following_handler)
    mediator.register(CreatePostRequest, create_post_handler)
    mediator.register(GetPostRequest, get_post_handler)
    mediator.register(DeletePostRequest, delete_post_handler)
    mediator.register(CreateCommentRequest, create_comment_handler)
    mediator.register(GetCommentsRequest, get_comments_handler)
    mediator.register(DeleteCommentRequest, delete_comment_handler)
    mediator.register(ToggleLikeRequest, toggle_like_handler)
    mediator.register(FollowUserRequest, follow_user_handler)
    mediator.register(UnfollowUserRequest, unfollow_user_handler)
    mediator.register(GetFeedRequest, get_feed_handler)
    mediator.register(CreateStoryRequest, create_story_handler)
    mediator.register(GetMyStoriesRequest, get_my_stories_handler)
    mediator.register(GetStoryFeedRequest, get_story_feed_handler)
    mediator.register(DeleteStoryRequest, delete_story_handler)
    mediator.register(SendMessageRequest, send_message_handler)
    mediator.register(GetConversationsRequest, get_conversations_handler)
    mediator.register(GetConversationRequest, get_conversation_handler)
    mediator.register(MarkMessagesReadRequest, mark_messages_read_handler)
    mediator.register(GetNotificationsRequest, get_notifications_handler)
    mediator.register(MarkNotificationReadRequest, mark_notification_read_handler)
    mediator.register(MarkAllReadRequest, mark_all_read_handler)
    mediator.register(SearchUsersRequest, search_users_handler)
    mediator.register(SearchHashtagsRequest, search_hashtags_handler)
    mediator.register(GetPostsByHashtagRequest, get_posts_by_hashtag_handler)


_register_handlers()


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(title="Instagram Clone - Vertical Slice Architecture", lifespan=lifespan)

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(post_router)
app.include_router(follow_router)
app.include_router(feed_router)
app.include_router(story_router)
app.include_router(message_router)
app.include_router(notification_router)
app.include_router(search_router)
