from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from layered.models.base import Base, TimestampMixin


class Comment(TimestampMixin, Base):
    __tablename__ = "comment"

    id: Mapped[int] = mapped_column(primary_key=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("post.id"), index=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("user.id"), index=True)
    content: Mapped[str] = mapped_column(Text)

    post: Mapped["Post"] = relationship(back_populates="comments")  # noqa: F821
    author: Mapped["User"] = relationship(back_populates="comments")  # noqa: F821
