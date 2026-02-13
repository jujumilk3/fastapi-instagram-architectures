from __future__ import annotations

from collections.abc import AsyncGenerator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from ddd.application.auth.service import AuthApplicationService
from ddd.application.feed.service import FeedApplicationService
from ddd.application.messaging.service import MessageApplicationService
from ddd.application.notification.service import NotificationApplicationService
from ddd.application.post.service import (
    CommentApplicationService,
    LikeApplicationService,
    PostApplicationService,
)
from ddd.application.search.service import SearchApplicationService
from ddd.application.social.service import (
    FollowApplicationService,
    StoryApplicationService,
)
from ddd.application.user.service import UserApplicationService
from ddd.infrastructure.database import async_session_factory
from ddd.infrastructure.repositories.hashtag_repository import SqlAlchemyHashtagRepository
from ddd.infrastructure.repositories.message_repository import SqlAlchemyMessageRepository
from ddd.infrastructure.repositories.notification_repository import SqlAlchemyNotificationRepository
from ddd.infrastructure.repositories.post_repository import (
    SqlAlchemyCommentRepository,
    SqlAlchemyLikeRepository,
    SqlAlchemyPostRepository,
)
from ddd.infrastructure.repositories.social_repository import (
    SqlAlchemyFollowRepository,
    SqlAlchemyStoryRepository,
)
from ddd.infrastructure.repositories.user_repository import SqlAlchemyUserRepository
from ddd.infrastructure.security import SecurityProvider

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
security = SecurityProvider()


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
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )
    return int(user_id)


def get_auth_service(
    db: AsyncSession = Depends(get_db),
) -> AuthApplicationService:
    return AuthApplicationService(SqlAlchemyUserRepository(db), security)


def get_user_service(
    db: AsyncSession = Depends(get_db),
) -> UserApplicationService:
    return UserApplicationService(
        SqlAlchemyUserRepository(db),
        SqlAlchemyFollowRepository(db),
        SqlAlchemyPostRepository(db),
    )


def get_post_service(
    db: AsyncSession = Depends(get_db),
) -> PostApplicationService:
    return PostApplicationService(
        SqlAlchemyPostRepository(db),
        SqlAlchemyUserRepository(db),
        SqlAlchemyLikeRepository(db),
        SqlAlchemyCommentRepository(db),
        SqlAlchemyHashtagRepository(db),
    )


def get_comment_service(
    db: AsyncSession = Depends(get_db),
) -> CommentApplicationService:
    return CommentApplicationService(
        SqlAlchemyCommentRepository(db),
        SqlAlchemyPostRepository(db),
        SqlAlchemyUserRepository(db),
        SqlAlchemyNotificationRepository(db),
    )


def get_like_service(
    db: AsyncSession = Depends(get_db),
) -> LikeApplicationService:
    return LikeApplicationService(
        SqlAlchemyLikeRepository(db),
        SqlAlchemyPostRepository(db),
        SqlAlchemyNotificationRepository(db),
    )


def get_follow_service(
    db: AsyncSession = Depends(get_db),
) -> FollowApplicationService:
    return FollowApplicationService(
        SqlAlchemyFollowRepository(db),
        SqlAlchemyUserRepository(db),
        SqlAlchemyNotificationRepository(db),
    )


def get_feed_service(
    db: AsyncSession = Depends(get_db),
) -> FeedApplicationService:
    return FeedApplicationService(
        SqlAlchemyPostRepository(db),
        SqlAlchemyFollowRepository(db),
        SqlAlchemyUserRepository(db),
        SqlAlchemyLikeRepository(db),
        SqlAlchemyCommentRepository(db),
    )


def get_story_service(
    db: AsyncSession = Depends(get_db),
) -> StoryApplicationService:
    return StoryApplicationService(
        SqlAlchemyStoryRepository(db),
        SqlAlchemyFollowRepository(db),
        SqlAlchemyUserRepository(db),
    )


def get_message_service(
    db: AsyncSession = Depends(get_db),
) -> MessageApplicationService:
    return MessageApplicationService(
        SqlAlchemyMessageRepository(db), SqlAlchemyUserRepository(db)
    )


def get_notification_service(
    db: AsyncSession = Depends(get_db),
) -> NotificationApplicationService:
    return NotificationApplicationService(SqlAlchemyNotificationRepository(db))


def get_search_service(
    db: AsyncSession = Depends(get_db),
) -> SearchApplicationService:
    return SearchApplicationService(
        SqlAlchemyUserRepository(db),
        SqlAlchemyHashtagRepository(db),
        SqlAlchemyLikeRepository(db),
        SqlAlchemyCommentRepository(db),
    )
