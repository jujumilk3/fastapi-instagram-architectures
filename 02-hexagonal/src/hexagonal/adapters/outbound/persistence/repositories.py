from datetime import datetime, timedelta, timezone

from sqlalchemy import and_, case, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from hexagonal.domain.entities.post import Comment, Like, Post
from hexagonal.domain.entities.social import Follow, Hashtag, Message, Notification, Story
from hexagonal.domain.entities.user import User
from hexagonal.adapters.outbound.persistence.models import (
    CommentModel, FollowModel, HashtagModel, LikeModel, MessageModel,
    NotificationModel, PostHashtagModel, PostModel, StoryModel, UserModel,
)
from hexagonal.ports.outbound.repositories import (
    CommentRepositoryPort, FollowRepositoryPort, HashtagRepositoryPort,
    LikeRepositoryPort, MessageRepositoryPort, NotificationRepositoryPort,
    PostRepositoryPort, StoryRepositoryPort, UserRepositoryPort,
)


# --- Mappers ---

def _user_to_entity(m: UserModel) -> User:
    return User(id=m.id, username=m.username, email=m.email, hashed_password=m.hashed_password,
                full_name=m.full_name, bio=m.bio, profile_image_url=m.profile_image_url,
                is_active=m.is_active, created_at=m.created_at, updated_at=m.updated_at)

def _post_to_entity(m: PostModel) -> Post:
    return Post(id=m.id, author_id=m.author_id, content=m.content, image_url=m.image_url,
                created_at=m.created_at, updated_at=m.updated_at)

def _comment_to_entity(m: CommentModel) -> Comment:
    return Comment(id=m.id, post_id=m.post_id, author_id=m.author_id, content=m.content, created_at=m.created_at)

def _like_to_entity(m: LikeModel) -> Like:
    return Like(id=m.id, post_id=m.post_id, user_id=m.user_id, created_at=m.created_at)

def _follow_to_entity(m: FollowModel) -> Follow:
    return Follow(id=m.id, follower_id=m.follower_id, following_id=m.following_id, created_at=m.created_at)

def _story_to_entity(m: StoryModel) -> Story:
    return Story(id=m.id, author_id=m.author_id, image_url=m.image_url, content=m.content, created_at=m.created_at)

def _message_to_entity(m: MessageModel) -> Message:
    return Message(id=m.id, sender_id=m.sender_id, receiver_id=m.receiver_id, content=m.content, is_read=m.is_read, created_at=m.created_at)

def _notification_to_entity(m: NotificationModel) -> Notification:
    return Notification(id=m.id, user_id=m.user_id, actor_id=m.actor_id, type=m.type,
                        reference_id=m.reference_id, message=m.message, is_read=m.is_read, created_at=m.created_at)

def _hashtag_to_entity(m: HashtagModel) -> Hashtag:
    return Hashtag(id=m.id, name=m.name, created_at=m.created_at)


class SqlAlchemyUserRepository(UserRepositoryPort):
    def __init__(self, db: AsyncSession): self.db = db

    async def create(self, user: User) -> User:
        m = UserModel(username=user.username, email=user.email, hashed_password=user.hashed_password, full_name=user.full_name)
        self.db.add(m); await self.db.flush(); await self.db.refresh(m)
        return _user_to_entity(m)

    async def get_by_id(self, user_id: int) -> User | None:
        m = await self.db.get(UserModel, user_id)
        return _user_to_entity(m) if m else None

    async def get_by_email(self, email: str) -> User | None:
        r = await self.db.execute(select(UserModel).where(UserModel.email == email))
        m = r.scalar_one_or_none()
        return _user_to_entity(m) if m else None

    async def get_by_username(self, username: str) -> User | None:
        r = await self.db.execute(select(UserModel).where(UserModel.username == username))
        m = r.scalar_one_or_none()
        return _user_to_entity(m) if m else None

    async def update(self, user: User) -> User:
        m = await self.db.get(UserModel, user.id)
        for attr in ("full_name", "bio", "profile_image_url"):
            setattr(m, attr, getattr(user, attr))
        await self.db.flush(); await self.db.refresh(m)
        return _user_to_entity(m)

    async def search(self, query: str, limit: int = 20) -> list[User]:
        r = await self.db.execute(select(UserModel).where(UserModel.username.ilike(f"%{query}%")).limit(limit))
        return [_user_to_entity(m) for m in r.scalars().all()]


class SqlAlchemyPostRepository(PostRepositoryPort):
    def __init__(self, db: AsyncSession): self.db = db

    async def create(self, post: Post) -> Post:
        m = PostModel(author_id=post.author_id, content=post.content, image_url=post.image_url)
        self.db.add(m); await self.db.flush(); await self.db.refresh(m)
        return _post_to_entity(m)

    async def get_by_id(self, post_id: int) -> Post | None:
        m = await self.db.get(PostModel, post_id)
        return _post_to_entity(m) if m else None

    async def get_by_author(self, author_id: int, limit: int, offset: int) -> list[Post]:
        r = await self.db.execute(select(PostModel).where(PostModel.author_id == author_id).order_by(PostModel.created_at.desc()).limit(limit).offset(offset))
        return [_post_to_entity(m) for m in r.scalars().all()]

    async def get_feed(self, following_ids: list[int], limit: int, offset: int) -> list[Post]:
        r = await self.db.execute(select(PostModel).where(PostModel.author_id.in_(following_ids)).order_by(PostModel.created_at.desc()).limit(limit).offset(offset))
        return [_post_to_entity(m) for m in r.scalars().all()]

    async def delete(self, post_id: int) -> None:
        m = await self.db.get(PostModel, post_id)
        if m: await self.db.delete(m); await self.db.flush()

    async def count_by_author(self, author_id: int) -> int:
        r = await self.db.execute(select(func.count()).select_from(PostModel).where(PostModel.author_id == author_id))
        return r.scalar_one()


class SqlAlchemyCommentRepository(CommentRepositoryPort):
    def __init__(self, db: AsyncSession): self.db = db

    async def create(self, comment: Comment) -> Comment:
        m = CommentModel(post_id=comment.post_id, author_id=comment.author_id, content=comment.content)
        self.db.add(m); await self.db.flush(); await self.db.refresh(m)
        return _comment_to_entity(m)

    async def get_by_id(self, comment_id: int) -> Comment | None:
        m = await self.db.get(CommentModel, comment_id)
        return _comment_to_entity(m) if m else None

    async def get_by_post(self, post_id: int, limit: int, offset: int) -> list[Comment]:
        r = await self.db.execute(select(CommentModel).where(CommentModel.post_id == post_id).order_by(CommentModel.created_at.desc()).limit(limit).offset(offset))
        return [_comment_to_entity(m) for m in r.scalars().all()]

    async def delete(self, comment_id: int) -> None:
        m = await self.db.get(CommentModel, comment_id)
        if m: await self.db.delete(m); await self.db.flush()


class SqlAlchemyLikeRepository(LikeRepositoryPort):
    def __init__(self, db: AsyncSession): self.db = db

    async def create(self, like: Like) -> Like:
        m = LikeModel(post_id=like.post_id, user_id=like.user_id)
        self.db.add(m); await self.db.flush(); await self.db.refresh(m)
        return _like_to_entity(m)

    async def get(self, post_id: int, user_id: int) -> Like | None:
        r = await self.db.execute(select(LikeModel).where(LikeModel.post_id == post_id, LikeModel.user_id == user_id))
        m = r.scalar_one_or_none()
        return _like_to_entity(m) if m else None

    async def delete(self, post_id: int, user_id: int) -> None:
        r = await self.db.execute(select(LikeModel).where(LikeModel.post_id == post_id, LikeModel.user_id == user_id))
        m = r.scalar_one_or_none()
        if m: await self.db.delete(m); await self.db.flush()

    async def count_by_post(self, post_id: int) -> int:
        r = await self.db.execute(select(func.count()).select_from(LikeModel).where(LikeModel.post_id == post_id))
        return r.scalar_one()


class SqlAlchemyFollowRepository(FollowRepositoryPort):
    def __init__(self, db: AsyncSession): self.db = db

    async def create(self, follow: Follow) -> Follow:
        m = FollowModel(follower_id=follow.follower_id, following_id=follow.following_id)
        self.db.add(m); await self.db.flush(); await self.db.refresh(m)
        return _follow_to_entity(m)

    async def get(self, follower_id: int, following_id: int) -> Follow | None:
        r = await self.db.execute(select(FollowModel).where(FollowModel.follower_id == follower_id, FollowModel.following_id == following_id))
        m = r.scalar_one_or_none()
        return _follow_to_entity(m) if m else None

    async def delete(self, follower_id: int, following_id: int) -> None:
        r = await self.db.execute(select(FollowModel).where(FollowModel.follower_id == follower_id, FollowModel.following_id == following_id))
        m = r.scalar_one_or_none()
        if m: await self.db.delete(m); await self.db.flush()

    async def get_followers(self, user_id: int) -> list[int]:
        r = await self.db.execute(select(FollowModel.follower_id).where(FollowModel.following_id == user_id))
        return list(r.scalars().all())

    async def get_following(self, user_id: int) -> list[int]:
        r = await self.db.execute(select(FollowModel.following_id).where(FollowModel.follower_id == user_id))
        return list(r.scalars().all())

    async def count_followers(self, user_id: int) -> int:
        r = await self.db.execute(select(func.count()).select_from(FollowModel).where(FollowModel.following_id == user_id))
        return r.scalar_one()

    async def count_following(self, user_id: int) -> int:
        r = await self.db.execute(select(func.count()).select_from(FollowModel).where(FollowModel.follower_id == user_id))
        return r.scalar_one()


class SqlAlchemyStoryRepository(StoryRepositoryPort):
    def __init__(self, db: AsyncSession): self.db = db

    async def create(self, story: Story) -> Story:
        m = StoryModel(author_id=story.author_id, image_url=story.image_url, content=story.content)
        self.db.add(m); await self.db.flush(); await self.db.refresh(m)
        return _story_to_entity(m)

    async def get_by_id(self, story_id: int) -> Story | None:
        m = await self.db.get(StoryModel, story_id)
        return _story_to_entity(m) if m else None

    async def get_active_by_author(self, author_id: int) -> list[Story]:
        cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
        r = await self.db.execute(select(StoryModel).where(StoryModel.author_id == author_id, StoryModel.created_at >= cutoff).order_by(StoryModel.created_at.desc()))
        return [_story_to_entity(m) for m in r.scalars().all()]

    async def get_feed(self, following_ids: list[int]) -> list[Story]:
        cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
        r = await self.db.execute(select(StoryModel).where(StoryModel.author_id.in_(following_ids), StoryModel.created_at >= cutoff).order_by(StoryModel.created_at.desc()))
        return [_story_to_entity(m) for m in r.scalars().all()]

    async def delete(self, story_id: int) -> None:
        m = await self.db.get(StoryModel, story_id)
        if m: await self.db.delete(m); await self.db.flush()


class SqlAlchemyMessageRepository(MessageRepositoryPort):
    def __init__(self, db: AsyncSession): self.db = db

    async def create(self, message: Message) -> Message:
        m = MessageModel(sender_id=message.sender_id, receiver_id=message.receiver_id, content=message.content)
        self.db.add(m); await self.db.flush(); await self.db.refresh(m)
        return _message_to_entity(m)

    async def get_conversation(self, user_id: int, other_user_id: int, limit: int, offset: int) -> list[Message]:
        r = await self.db.execute(
            select(MessageModel).where(or_(
                and_(MessageModel.sender_id == user_id, MessageModel.receiver_id == other_user_id),
                and_(MessageModel.sender_id == other_user_id, MessageModel.receiver_id == user_id),
            )).order_by(MessageModel.created_at.desc()).limit(limit).offset(offset))
        return [_message_to_entity(m) for m in r.scalars().all()]

    async def get_conversations(self, user_id: int) -> list[dict]:
        other_user = case((MessageModel.sender_id == user_id, MessageModel.receiver_id), else_=MessageModel.sender_id)
        subq = select(other_user.label("other_user_id"), func.max(MessageModel.id).label("last_message_id")).where(
            or_(MessageModel.sender_id == user_id, MessageModel.receiver_id == user_id)).group_by(other_user).subquery()
        r = await self.db.execute(select(MessageModel).join(subq, MessageModel.id == subq.c.last_message_id).order_by(MessageModel.created_at.desc()))
        return [{"other_user_id": m.receiver_id if m.sender_id == user_id else m.sender_id,
                 "last_message": _message_to_entity(m)} for m in r.scalars().all()]

    async def mark_as_read(self, user_id: int, sender_id: int) -> None:
        r = await self.db.execute(select(MessageModel).where(MessageModel.sender_id == sender_id, MessageModel.receiver_id == user_id, MessageModel.is_read.is_(False)))
        for m in r.scalars().all(): m.is_read = True
        await self.db.flush()


class SqlAlchemyNotificationRepository(NotificationRepositoryPort):
    def __init__(self, db: AsyncSession): self.db = db

    async def create(self, notification: Notification) -> Notification:
        m = NotificationModel(user_id=notification.user_id, actor_id=notification.actor_id, type=notification.type,
                              reference_id=notification.reference_id, message=notification.message)
        self.db.add(m); await self.db.flush(); await self.db.refresh(m)
        return _notification_to_entity(m)

    async def get_by_user(self, user_id: int, limit: int, offset: int) -> list[Notification]:
        r = await self.db.execute(select(NotificationModel).where(NotificationModel.user_id == user_id).order_by(NotificationModel.created_at.desc()).limit(limit).offset(offset))
        return [_notification_to_entity(m) for m in r.scalars().all()]

    async def mark_read(self, notification_id: int, user_id: int) -> None:
        await self.db.execute(update(NotificationModel).where(NotificationModel.id == notification_id, NotificationModel.user_id == user_id).values(is_read=True))
        await self.db.flush()

    async def mark_all_read(self, user_id: int) -> None:
        await self.db.execute(update(NotificationModel).where(NotificationModel.user_id == user_id, NotificationModel.is_read.is_(False)).values(is_read=True))
        await self.db.flush()


class SqlAlchemyHashtagRepository(HashtagRepositoryPort):
    def __init__(self, db: AsyncSession): self.db = db

    async def get_or_create(self, name: str) -> Hashtag:
        r = await self.db.execute(select(HashtagModel).where(HashtagModel.name == name))
        m = r.scalar_one_or_none()
        if not m:
            m = HashtagModel(name=name)
            self.db.add(m); await self.db.flush(); await self.db.refresh(m)
        return _hashtag_to_entity(m)

    async def link_post(self, post_id: int, hashtag_id: int) -> None:
        r = await self.db.execute(select(PostHashtagModel).where(PostHashtagModel.post_id == post_id, PostHashtagModel.hashtag_id == hashtag_id))
        if not r.scalar_one_or_none():
            self.db.add(PostHashtagModel(post_id=post_id, hashtag_id=hashtag_id)); await self.db.flush()

    async def unlink_post(self, post_id: int) -> None:
        r = await self.db.execute(select(PostHashtagModel).where(PostHashtagModel.post_id == post_id))
        for m in r.scalars().all(): await self.db.delete(m)
        await self.db.flush()

    async def search(self, query: str, limit: int) -> list[Hashtag]:
        r = await self.db.execute(select(HashtagModel).where(HashtagModel.name.ilike(f"%{query}%")).limit(limit))
        return [_hashtag_to_entity(m) for m in r.scalars().all()]

    async def get_posts_by_hashtag(self, tag: str, limit: int, offset: int) -> list[Post]:
        r = await self.db.execute(
            select(PostModel).join(PostHashtagModel, PostModel.id == PostHashtagModel.post_id)
            .join(HashtagModel, PostHashtagModel.hashtag_id == HashtagModel.id)
            .where(HashtagModel.name == tag).order_by(PostModel.created_at.desc()).limit(limit).offset(offset))
        return [_post_to_entity(m) for m in r.scalars().all()]
