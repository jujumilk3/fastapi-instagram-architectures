from collections.abc import AsyncGenerator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from clean.frameworks.database import async_session_factory
from clean.frameworks.security import JwtBcryptSecurity
from clean.interface_adapters.gateways.repositories import (
    SqlAlchemyCommentRepository, SqlAlchemyFollowRepository, SqlAlchemyHashtagRepository,
    SqlAlchemyLikeRepository, SqlAlchemyMessageRepository, SqlAlchemyNotificationRepository,
    SqlAlchemyPostRepository, SqlAlchemyStoryRepository, SqlAlchemyUserRepository,
)
from clean.use_cases.auth.get_me import GetMeUseCase
from clean.use_cases.auth.login import LoginUseCase
from clean.use_cases.auth.register import RegisterUseCase
from clean.use_cases.comment.create_comment import CreateCommentUseCase
from clean.use_cases.comment.delete_comment import DeleteCommentUseCase
from clean.use_cases.comment.get_comments import GetCommentsUseCase
from clean.use_cases.feed.get_feed import GetFeedUseCase
from clean.use_cases.follow.follow_user import FollowUserUseCase
from clean.use_cases.follow.unfollow_user import UnfollowUserUseCase
from clean.use_cases.like.toggle_like import ToggleLikeUseCase
from clean.use_cases.message.get_conversation import GetConversationUseCase
from clean.use_cases.message.get_conversations import GetConversationsUseCase
from clean.use_cases.message.mark_read import MarkMessagesReadUseCase
from clean.use_cases.message.send_message import SendMessageUseCase
from clean.use_cases.notification.get_notifications import GetNotificationsUseCase
from clean.use_cases.notification.mark_all_read import MarkAllNotificationsReadUseCase
from clean.use_cases.notification.mark_read import MarkNotificationReadUseCase
from clean.use_cases.post.create_post import CreatePostUseCase
from clean.use_cases.post.delete_post import DeletePostUseCase
from clean.use_cases.post.get_post import GetPostUseCase
from clean.use_cases.post.get_user_posts import GetUserPostsUseCase
from clean.use_cases.search.get_posts_by_hashtag import GetPostsByHashtagUseCase
from clean.use_cases.search.search_hashtags import SearchHashtagsUseCase
from clean.use_cases.search.search_users import SearchUsersUseCase
from clean.use_cases.story.create_story import CreateStoryUseCase
from clean.use_cases.story.delete_story import DeleteStoryUseCase
from clean.use_cases.story.get_my_stories import GetMyStoriesUseCase
from clean.use_cases.story.get_story_feed import GetStoryFeedUseCase
from clean.use_cases.user.get_followers import GetFollowersUseCase
from clean.use_cases.user.get_following import GetFollowingUseCase
from clean.use_cases.user.get_profile import GetProfileUseCase
from clean.use_cases.user.update_profile import UpdateProfileUseCase

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
security = JwtBcryptSecurity()


async def get_db() -> AsyncGenerator[AsyncSession]:
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def get_current_user_id(token: str = Depends(oauth2_scheme)) -> int:
    payload = security.decode_token(token)
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return int(user_id)


# --- Auth use cases ---

def get_register_uc(db: AsyncSession = Depends(get_db)) -> RegisterUseCase:
    return RegisterUseCase(SqlAlchemyUserRepository(db), security)

def get_login_uc(db: AsyncSession = Depends(get_db)) -> LoginUseCase:
    return LoginUseCase(SqlAlchemyUserRepository(db), security)

def get_me_uc(db: AsyncSession = Depends(get_db)) -> GetMeUseCase:
    return GetMeUseCase(SqlAlchemyUserRepository(db))


# --- User use cases ---

def get_profile_uc(db: AsyncSession = Depends(get_db)) -> GetProfileUseCase:
    return GetProfileUseCase(SqlAlchemyUserRepository(db), SqlAlchemyFollowRepository(db), SqlAlchemyPostRepository(db))

def get_update_profile_uc(db: AsyncSession = Depends(get_db)) -> UpdateProfileUseCase:
    return UpdateProfileUseCase(SqlAlchemyUserRepository(db))

def get_followers_uc(db: AsyncSession = Depends(get_db)) -> GetFollowersUseCase:
    return GetFollowersUseCase(SqlAlchemyUserRepository(db), SqlAlchemyFollowRepository(db))

def get_following_uc(db: AsyncSession = Depends(get_db)) -> GetFollowingUseCase:
    return GetFollowingUseCase(SqlAlchemyUserRepository(db), SqlAlchemyFollowRepository(db))


# --- Post use cases ---

def get_create_post_uc(db: AsyncSession = Depends(get_db)) -> CreatePostUseCase:
    return CreatePostUseCase(
        SqlAlchemyPostRepository(db), SqlAlchemyUserRepository(db),
        SqlAlchemyLikeRepository(db), SqlAlchemyCommentRepository(db), SqlAlchemyHashtagRepository(db),
    )

def get_get_post_uc(db: AsyncSession = Depends(get_db)) -> GetPostUseCase:
    return GetPostUseCase(SqlAlchemyPostRepository(db), SqlAlchemyUserRepository(db), SqlAlchemyLikeRepository(db), SqlAlchemyCommentRepository(db))

def get_user_posts_uc(db: AsyncSession = Depends(get_db)) -> GetUserPostsUseCase:
    return GetUserPostsUseCase(SqlAlchemyPostRepository(db), SqlAlchemyUserRepository(db), SqlAlchemyLikeRepository(db), SqlAlchemyCommentRepository(db))

def get_delete_post_uc(db: AsyncSession = Depends(get_db)) -> DeletePostUseCase:
    return DeletePostUseCase(SqlAlchemyPostRepository(db), SqlAlchemyHashtagRepository(db))


# --- Comment use cases ---

def get_create_comment_uc(db: AsyncSession = Depends(get_db)) -> CreateCommentUseCase:
    return CreateCommentUseCase(SqlAlchemyCommentRepository(db), SqlAlchemyPostRepository(db), SqlAlchemyUserRepository(db), SqlAlchemyNotificationRepository(db))

def get_comments_uc(db: AsyncSession = Depends(get_db)) -> GetCommentsUseCase:
    return GetCommentsUseCase(SqlAlchemyCommentRepository(db), SqlAlchemyUserRepository(db))

def get_delete_comment_uc(db: AsyncSession = Depends(get_db)) -> DeleteCommentUseCase:
    return DeleteCommentUseCase(SqlAlchemyCommentRepository(db))


# --- Like use case ---

def get_toggle_like_uc(db: AsyncSession = Depends(get_db)) -> ToggleLikeUseCase:
    return ToggleLikeUseCase(SqlAlchemyLikeRepository(db), SqlAlchemyPostRepository(db), SqlAlchemyNotificationRepository(db))


# --- Follow use cases ---

def get_follow_user_uc(db: AsyncSession = Depends(get_db)) -> FollowUserUseCase:
    return FollowUserUseCase(SqlAlchemyFollowRepository(db), SqlAlchemyUserRepository(db), SqlAlchemyNotificationRepository(db))

def get_unfollow_user_uc(db: AsyncSession = Depends(get_db)) -> UnfollowUserUseCase:
    return UnfollowUserUseCase(SqlAlchemyFollowRepository(db))


# --- Feed use case ---

def get_feed_uc(db: AsyncSession = Depends(get_db)) -> GetFeedUseCase:
    return GetFeedUseCase(
        SqlAlchemyPostRepository(db), SqlAlchemyFollowRepository(db),
        SqlAlchemyUserRepository(db), SqlAlchemyLikeRepository(db), SqlAlchemyCommentRepository(db),
    )


# --- Story use cases ---

def get_create_story_uc(db: AsyncSession = Depends(get_db)) -> CreateStoryUseCase:
    return CreateStoryUseCase(SqlAlchemyStoryRepository(db))

def get_my_stories_uc(db: AsyncSession = Depends(get_db)) -> GetMyStoriesUseCase:
    return GetMyStoriesUseCase(SqlAlchemyStoryRepository(db), SqlAlchemyUserRepository(db))

def get_story_feed_uc(db: AsyncSession = Depends(get_db)) -> GetStoryFeedUseCase:
    return GetStoryFeedUseCase(SqlAlchemyStoryRepository(db), SqlAlchemyFollowRepository(db), SqlAlchemyUserRepository(db))

def get_delete_story_uc(db: AsyncSession = Depends(get_db)) -> DeleteStoryUseCase:
    return DeleteStoryUseCase(SqlAlchemyStoryRepository(db))


# --- Message use cases ---

def get_send_message_uc(db: AsyncSession = Depends(get_db)) -> SendMessageUseCase:
    return SendMessageUseCase(SqlAlchemyMessageRepository(db), SqlAlchemyUserRepository(db))

def get_conversations_uc(db: AsyncSession = Depends(get_db)) -> GetConversationsUseCase:
    return GetConversationsUseCase(SqlAlchemyMessageRepository(db))

def get_conversation_uc(db: AsyncSession = Depends(get_db)) -> GetConversationUseCase:
    return GetConversationUseCase(SqlAlchemyMessageRepository(db))

def get_mark_messages_read_uc(db: AsyncSession = Depends(get_db)) -> MarkMessagesReadUseCase:
    return MarkMessagesReadUseCase(SqlAlchemyMessageRepository(db))


# --- Notification use cases ---

def get_notifications_uc(db: AsyncSession = Depends(get_db)) -> GetNotificationsUseCase:
    return GetNotificationsUseCase(SqlAlchemyNotificationRepository(db))

def get_mark_notification_read_uc(db: AsyncSession = Depends(get_db)) -> MarkNotificationReadUseCase:
    return MarkNotificationReadUseCase(SqlAlchemyNotificationRepository(db))

def get_mark_all_notifications_read_uc(db: AsyncSession = Depends(get_db)) -> MarkAllNotificationsReadUseCase:
    return MarkAllNotificationsReadUseCase(SqlAlchemyNotificationRepository(db))


# --- Search use cases ---

def get_search_users_uc(db: AsyncSession = Depends(get_db)) -> SearchUsersUseCase:
    return SearchUsersUseCase(SqlAlchemyUserRepository(db))

def get_search_hashtags_uc(db: AsyncSession = Depends(get_db)) -> SearchHashtagsUseCase:
    return SearchHashtagsUseCase(SqlAlchemyHashtagRepository(db))

def get_posts_by_hashtag_uc(db: AsyncSession = Depends(get_db)) -> GetPostsByHashtagUseCase:
    return GetPostsByHashtagUseCase(
        SqlAlchemyHashtagRepository(db), SqlAlchemyUserRepository(db),
        SqlAlchemyLikeRepository(db), SqlAlchemyCommentRepository(db),
    )
