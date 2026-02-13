from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from layered.models.base import Base, TimestampMixin


class Story(TimestampMixin, Base):
    __tablename__ = "story"

    id: Mapped[int] = mapped_column(primary_key=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("user.id"), index=True)
    image_url: Mapped[str | None] = mapped_column(String(500))
    content: Mapped[str | None] = mapped_column(Text)

    author: Mapped["User"] = relationship(back_populates="stories")  # noqa: F821
