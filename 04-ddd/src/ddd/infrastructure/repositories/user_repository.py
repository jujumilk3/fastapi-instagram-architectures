from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ddd.domain.user.aggregate import UserAggregate
from ddd.domain.user.repository import UserRepository
from ddd.infrastructure.orm.mapper import user_model_to_aggregate
from ddd.infrastructure.orm.models import UserModel


class SqlAlchemyUserRepository(UserRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, user: UserAggregate) -> UserAggregate:
        m = UserModel(
            username=user.username.value,
            email=user.email.value,
            hashed_password=user.hashed_password,
            full_name=user.full_name,
        )
        self.db.add(m)
        await self.db.flush()
        await self.db.refresh(m)
        return user_model_to_aggregate(m)

    async def get_by_id(self, user_id: int) -> UserAggregate | None:
        m = await self.db.get(UserModel, user_id)
        return user_model_to_aggregate(m) if m else None

    async def get_by_email(self, email: str) -> UserAggregate | None:
        r = await self.db.execute(
            select(UserModel).where(UserModel.email == email)
        )
        m = r.scalar_one_or_none()
        return user_model_to_aggregate(m) if m else None

    async def get_by_username(self, username: str) -> UserAggregate | None:
        r = await self.db.execute(
            select(UserModel).where(UserModel.username == username)
        )
        m = r.scalar_one_or_none()
        return user_model_to_aggregate(m) if m else None

    async def update(self, user: UserAggregate) -> UserAggregate:
        m = await self.db.get(UserModel, user.id)
        for attr in ("full_name", "bio", "profile_image_url"):
            setattr(m, attr, getattr(user, attr))
        await self.db.flush()
        await self.db.refresh(m)
        return user_model_to_aggregate(m)

    async def search(self, query: str, limit: int = 20) -> list[UserAggregate]:
        r = await self.db.execute(
            select(UserModel)
            .where(UserModel.username.ilike(f"%{query}%"))
            .limit(limit)
        )
        return [user_model_to_aggregate(m) for m in r.scalars().all()]
