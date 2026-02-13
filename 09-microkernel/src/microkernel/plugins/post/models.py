from sqlalchemy import Boolean, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from microkernel.core.base_model import Base, TimestampMixin


class Post(TimestampMixin, Base):
    __tablename__ = "post"

    id: Mapped[int] = mapped_column(primary_key=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("user.id"), index=True)
    content: Mapped[str | None] = mapped_column(Text)
    image_url: Mapped[str | None] = mapped_column(String(500))


class Comment(TimestampMixin, Base):
    __tablename__ = "comment"

    id: Mapped[int] = mapped_column(primary_key=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("post.id"), index=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("user.id"), index=True)
    content: Mapped[str] = mapped_column(Text)


class Like(TimestampMixin, Base):
    __tablename__ = "like"
    __table_args__ = (UniqueConstraint("post_id", "user_id", name="uq_like_post_user"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("post.id"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), index=True)


class Hashtag(TimestampMixin, Base):
    __tablename__ = "hashtag"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)


class PostHashtag(Base):
    __tablename__ = "post_hashtag"

    id: Mapped[int] = mapped_column(primary_key=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("post.id"), index=True)
    hashtag_id: Mapped[int] = mapped_column(ForeignKey("hashtag.id"), index=True)
