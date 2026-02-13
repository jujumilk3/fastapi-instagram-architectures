from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from layered.models.base import Base, TimestampMixin


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

    post: Mapped["Post"] = relationship(back_populates="hashtags")  # noqa: F821
    hashtag: Mapped["Hashtag"] = relationship(back_populates="posts")
