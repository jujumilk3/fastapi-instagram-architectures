from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from layered.models.base import Base, TimestampMixin


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

    posts: Mapped[list["Post"]] = relationship(back_populates="author", cascade="all, delete-orphan")  # noqa: F821
    comments: Mapped[list["Comment"]] = relationship(back_populates="author", cascade="all, delete-orphan")  # noqa: F821
    stories: Mapped[list["Story"]] = relationship(back_populates="author", cascade="all, delete-orphan")  # noqa: F821
