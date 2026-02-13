from collections.abc import AsyncGenerator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from hexagonal.adapters.outbound.persistence.repositories import (
    SqlAlchemyCommentRepository, SqlAlchemyFollowRepository, SqlAlchemyHashtagRepository,
    SqlAlchemyLikeRepository, SqlAlchemyMessageRepository, SqlAlchemyNotificationRepository,
    SqlAlchemyPostRepository, SqlAlchemyStoryRepository, SqlAlchemyUserRepository,
)
from hexagonal.adapters.outbound.security.jwt_bcrypt import JwtBcryptSecurity
from hexagonal.application.auth_service import (
    AuthService, CommentService, FeedService, FollowService, LikeService,
    MessageService, NotificationService, PostService, SearchService, StoryService, UserService,
)

DATABASE_URL = "sqlite+aiosqlite:///./hexagonal.db"
engine = create_async_engine(DATABASE_URL, echo=False)
async_session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

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


def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(SqlAlchemyUserRepository(db), security)

def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(SqlAlchemyUserRepository(db), SqlAlchemyFollowRepository(db), SqlAlchemyPostRepository(db))

def get_post_service(db: AsyncSession = Depends(get_db)) -> PostService:
    return PostService(SqlAlchemyPostRepository(db), SqlAlchemyUserRepository(db), SqlAlchemyLikeRepository(db), SqlAlchemyCommentRepository(db), SqlAlchemyHashtagRepository(db))

def get_comment_service(db: AsyncSession = Depends(get_db)) -> CommentService:
    return CommentService(SqlAlchemyCommentRepository(db), SqlAlchemyPostRepository(db), SqlAlchemyUserRepository(db), SqlAlchemyNotificationRepository(db))

def get_like_service(db: AsyncSession = Depends(get_db)) -> LikeService:
    return LikeService(SqlAlchemyLikeRepository(db), SqlAlchemyPostRepository(db), SqlAlchemyNotificationRepository(db))

def get_follow_service(db: AsyncSession = Depends(get_db)) -> FollowService:
    return FollowService(SqlAlchemyFollowRepository(db), SqlAlchemyUserRepository(db), SqlAlchemyNotificationRepository(db))

def get_feed_service(db: AsyncSession = Depends(get_db)) -> FeedService:
    return FeedService(SqlAlchemyPostRepository(db), SqlAlchemyFollowRepository(db), SqlAlchemyUserRepository(db), SqlAlchemyLikeRepository(db), SqlAlchemyCommentRepository(db))

def get_story_service(db: AsyncSession = Depends(get_db)) -> StoryService:
    return StoryService(SqlAlchemyStoryRepository(db), SqlAlchemyFollowRepository(db), SqlAlchemyUserRepository(db))

def get_message_service(db: AsyncSession = Depends(get_db)) -> MessageService:
    return MessageService(SqlAlchemyMessageRepository(db), SqlAlchemyUserRepository(db))

def get_notification_service(db: AsyncSession = Depends(get_db)) -> NotificationService:
    return NotificationService(SqlAlchemyNotificationRepository(db))

def get_search_service(db: AsyncSession = Depends(get_db)) -> SearchService:
    return SearchService(SqlAlchemyUserRepository(db), SqlAlchemyHashtagRepository(db), SqlAlchemyLikeRepository(db), SqlAlchemyCommentRepository(db))
