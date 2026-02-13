from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession


@dataclass
class GetUserById:
    user_id: int
    db: AsyncSession


@dataclass
class GetUserByEmail:
    email: str
    db: AsyncSession


@dataclass
class GetUserProfile:
    user_id: int
    db: AsyncSession


@dataclass
class GetUserPosts:
    user_id: int
    limit: int
    offset: int
    db: AsyncSession


@dataclass
class GetUserFollowers:
    user_id: int
    db: AsyncSession


@dataclass
class GetUserFollowing:
    user_id: int
    db: AsyncSession


@dataclass
class GetPost:
    post_id: int
    db: AsyncSession


@dataclass
class GetPostComments:
    post_id: int
    limit: int
    offset: int
    db: AsyncSession


@dataclass
class GetFeed:
    user_id: int
    limit: int
    offset: int
    db: AsyncSession


@dataclass
class GetMyStories:
    user_id: int
    db: AsyncSession


@dataclass
class GetStoryFeed:
    user_id: int
    db: AsyncSession


@dataclass
class GetConversations:
    user_id: int
    db: AsyncSession


@dataclass
class GetConversation:
    user_id: int
    other_user_id: int
    limit: int
    offset: int
    db: AsyncSession


@dataclass
class GetNotifications:
    user_id: int
    limit: int
    offset: int
    db: AsyncSession


@dataclass
class SearchUsers:
    query: str
    limit: int
    db: AsyncSession


@dataclass
class SearchHashtags:
    query: str
    limit: int
    db: AsyncSession


@dataclass
class GetPostsByHashtag:
    tag: str
    limit: int
    offset: int
    db: AsyncSession
