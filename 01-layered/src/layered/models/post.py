from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from layered.models.base import Base, TimestampMixin


class Post(TimestampMixin, Base):
    __tablename__ = "post"

    id: Mapped[int] = mapped_column(primary_key=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("user.id"), index=True)
    content: Mapped[str | None] = mapped_column(Text)
    image_url: Mapped[str | None] = mapped_column(String(500))

    author: Mapped["User"] = relationship(back_populates="posts")  # noqa: F821
    comments: Mapped[list["Comment"]] = relationship(back_populates="post", cascade="all, delete-orphan")  # noqa: F821
    likes: Mapped[list["Like"]] = relationship(back_populates="post", cascade="all, delete-orphan")  # noqa: F821
    hashtags: Mapped[list["PostHashtag"]] = relationship(back_populates="post", cascade="all, delete-orphan")  # noqa: F821
