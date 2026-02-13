from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from cqrs_es.shared.database import Base


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class UserProjection(TimestampMixin, Base):
    __tablename__ = "user_projection"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str | None] = mapped_column(String(100))
    bio: Mapped[str | None] = mapped_column(String(500))
    profile_image_url: Mapped[str | None] = mapped_column(String(500))
    is_active: Mapped[bool] = mapped_column(default=True)
    post_count: Mapped[int] = mapped_column(Integer, default=0)
    follower_count: Mapped[int] = mapped_column(Integer, default=0)
    following_count: Mapped[int] = mapped_column(Integer, default=0)


class PostProjection(TimestampMixin, Base):
    __tablename__ = "post_projection"

    id: Mapped[int] = mapped_column(primary_key=True)
    author_id: Mapped[int] = mapped_column(index=True)
    author_username: Mapped[str | None] = mapped_column(String(50))
    content: Mapped[str | None] = mapped_column(Text)
    image_url: Mapped[str | None] = mapped_column(String(500))
    like_count: Mapped[int] = mapped_column(Integer, default=0)
    comment_count: Mapped[int] = mapped_column(Integer, default=0)


class CommentProjection(TimestampMixin, Base):
    __tablename__ = "comment_projection"

    id: Mapped[int] = mapped_column(primary_key=True)
    post_id: Mapped[int] = mapped_column(index=True)
    author_id: Mapped[int] = mapped_column(index=True)
    author_username: Mapped[str | None] = mapped_column(String(50))
    content: Mapped[str] = mapped_column(Text)


class LikeProjection(Base):
    __tablename__ = "like_projection"
    __table_args__ = (UniqueConstraint("post_id", "user_id", name="uq_like_proj"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    post_id: Mapped[int] = mapped_column(index=True)
    user_id: Mapped[int] = mapped_column(index=True)


class FollowProjection(Base):
    __tablename__ = "follow_projection"
    __table_args__ = (UniqueConstraint("follower_id", "following_id", name="uq_follow_proj"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    follower_id: Mapped[int] = mapped_column(index=True)
    following_id: Mapped[int] = mapped_column(index=True)


class StoryProjection(TimestampMixin, Base):
    __tablename__ = "story_projection"

    id: Mapped[int] = mapped_column(primary_key=True)
    author_id: Mapped[int] = mapped_column(index=True)
    author_username: Mapped[str | None] = mapped_column(String(50))
    image_url: Mapped[str | None] = mapped_column(String(500))
    content: Mapped[str | None] = mapped_column(Text)


class MessageProjection(TimestampMixin, Base):
    __tablename__ = "message_projection"

    id: Mapped[int] = mapped_column(primary_key=True)
    sender_id: Mapped[int] = mapped_column(index=True)
    receiver_id: Mapped[int] = mapped_column(index=True)
    content: Mapped[str] = mapped_column(Text)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)


class NotificationProjection(TimestampMixin, Base):
    __tablename__ = "notification_projection"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(index=True)
    actor_id: Mapped[int] = mapped_column(index=True)
    type: Mapped[str] = mapped_column(String(50))
    reference_id: Mapped[int | None] = mapped_column()
    message: Mapped[str] = mapped_column(Text)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)


class HashtagProjection(Base):
    __tablename__ = "hashtag_projection"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)


class PostHashtagProjection(Base):
    __tablename__ = "post_hashtag_projection"
    __table_args__ = (UniqueConstraint("post_id", "hashtag_id", name="uq_post_hashtag_proj"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("post_projection.id"), index=True)
    hashtag_id: Mapped[int] = mapped_column(ForeignKey("hashtag_projection.id"), index=True)
