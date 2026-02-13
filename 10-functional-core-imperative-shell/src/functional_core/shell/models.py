from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        default=None,
        onupdate=lambda: datetime.now(timezone.utc),
    )


class User(TimestampMixin, Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str | None] = mapped_column(String(100))
    bio: Mapped[str | None] = mapped_column(String(500))
    profile_image_url: Mapped[str | None] = mapped_column(String(500))
    is_active: Mapped[bool] = mapped_column(default=True)

    posts: Mapped[list["Post"]] = relationship(back_populates="author", cascade="all, delete-orphan")
    comments: Mapped[list["Comment"]] = relationship(back_populates="author", cascade="all, delete-orphan")
    stories: Mapped[list["Story"]] = relationship(back_populates="author", cascade="all, delete-orphan")


class Post(TimestampMixin, Base):
    __tablename__ = "post"

    id: Mapped[int] = mapped_column(primary_key=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("user.id"), index=True)
    content: Mapped[str | None] = mapped_column(Text)
    image_url: Mapped[str | None] = mapped_column(String(500))

    author: Mapped["User"] = relationship(back_populates="posts")
    comments: Mapped[list["Comment"]] = relationship(back_populates="post", cascade="all, delete-orphan")
    likes: Mapped[list["Like"]] = relationship(back_populates="post", cascade="all, delete-orphan")
    hashtags: Mapped[list["PostHashtag"]] = relationship(back_populates="post", cascade="all, delete-orphan")


class Comment(TimestampMixin, Base):
    __tablename__ = "comment"

    id: Mapped[int] = mapped_column(primary_key=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("post.id"), index=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("user.id"), index=True)
    content: Mapped[str] = mapped_column(Text)

    post: Mapped["Post"] = relationship(back_populates="comments")
    author: Mapped["User"] = relationship(back_populates="comments")


class Like(TimestampMixin, Base):
    __tablename__ = "like"
    __table_args__ = (UniqueConstraint("post_id", "user_id", name="uq_like_post_user"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("post.id"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), index=True)

    post: Mapped["Post"] = relationship(back_populates="likes")


class Follow(TimestampMixin, Base):
    __tablename__ = "follow"
    __table_args__ = (UniqueConstraint("follower_id", "following_id", name="uq_follow"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    follower_id: Mapped[int] = mapped_column(ForeignKey("user.id"), index=True)
    following_id: Mapped[int] = mapped_column(ForeignKey("user.id"), index=True)


class Hashtag(TimestampMixin, Base):
    __tablename__ = "hashtag"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)

    posts: Mapped[list["PostHashtag"]] = relationship(back_populates="hashtag")


class PostHashtag(Base):
    __tablename__ = "post_hashtag"
    __table_args__ = (UniqueConstraint("post_id", "hashtag_id", name="uq_post_hashtag"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("post.id"), index=True)
    hashtag_id: Mapped[int] = mapped_column(ForeignKey("hashtag.id"), index=True)

    post: Mapped["Post"] = relationship(back_populates="hashtags")
    hashtag: Mapped["Hashtag"] = relationship(back_populates="posts")


class Story(TimestampMixin, Base):
    __tablename__ = "story"

    id: Mapped[int] = mapped_column(primary_key=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("user.id"), index=True)
    image_url: Mapped[str | None] = mapped_column(String(500))
    content: Mapped[str | None] = mapped_column(Text)

    author: Mapped["User"] = relationship(back_populates="stories")


class Message(TimestampMixin, Base):
    __tablename__ = "message"

    id: Mapped[int] = mapped_column(primary_key=True)
    sender_id: Mapped[int] = mapped_column(ForeignKey("user.id"), index=True)
    receiver_id: Mapped[int] = mapped_column(ForeignKey("user.id"), index=True)
    content: Mapped[str] = mapped_column(Text)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)


class Notification(TimestampMixin, Base):
    __tablename__ = "notification"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), index=True)
    actor_id: Mapped[int] = mapped_column(ForeignKey("user.id"), index=True)
    type: Mapped[str] = mapped_column(String(50))
    reference_id: Mapped[int | None] = mapped_column()
    message: Mapped[str] = mapped_column(Text)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
