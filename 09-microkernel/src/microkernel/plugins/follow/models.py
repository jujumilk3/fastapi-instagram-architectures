from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from microkernel.core.base_model import Base, TimestampMixin


class Follow(TimestampMixin, Base):
    __tablename__ = "follow"
    __table_args__ = (UniqueConstraint("follower_id", "following_id", name="uq_follow"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    follower_id: Mapped[int] = mapped_column(ForeignKey("user.id"), index=True)
    following_id: Mapped[int] = mapped_column(ForeignKey("user.id"), index=True)
