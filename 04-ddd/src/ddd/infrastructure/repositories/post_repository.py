from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ddd.domain.post.aggregate import PostAggregate
from ddd.domain.post.entities import Comment, Like
from ddd.domain.post.repository import CommentRepository, LikeRepository, PostRepository
from ddd.infrastructure.orm.mapper import (
    comment_model_to_entity,
    like_model_to_entity,
    post_model_to_aggregate,
)
from ddd.infrastructure.orm.models import CommentModel, LikeModel, PostModel


class SqlAlchemyPostRepository(PostRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, post: PostAggregate) -> PostAggregate:
        m = PostModel(
            author_id=post.author_id,
            content=post.content,
            image_url=post.image_url,
        )
        self.db.add(m)
        await self.db.flush()
        await self.db.refresh(m)
        return post_model_to_aggregate(m)

    async def get_by_id(self, post_id: int) -> PostAggregate | None:
        m = await self.db.get(PostModel, post_id)
        return post_model_to_aggregate(m) if m else None

    async def get_by_author(
        self, author_id: int, limit: int, offset: int
    ) -> list[PostAggregate]:
        r = await self.db.execute(
            select(PostModel)
            .where(PostModel.author_id == author_id)
            .order_by(PostModel.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return [post_model_to_aggregate(m) for m in r.scalars().all()]

    async def get_feed(
        self, following_ids: list[int], limit: int, offset: int
    ) -> list[PostAggregate]:
        r = await self.db.execute(
            select(PostModel)
            .where(PostModel.author_id.in_(following_ids))
            .order_by(PostModel.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return [post_model_to_aggregate(m) for m in r.scalars().all()]

    async def delete(self, post_id: int) -> None:
        m = await self.db.get(PostModel, post_id)
        if m:
            await self.db.delete(m)
            await self.db.flush()

    async def count_by_author(self, author_id: int) -> int:
        r = await self.db.execute(
            select(func.count())
            .select_from(PostModel)
            .where(PostModel.author_id == author_id)
        )
        return r.scalar_one()


class SqlAlchemyCommentRepository(CommentRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, comment: Comment) -> Comment:
        m = CommentModel(
            post_id=comment.post_id,
            author_id=comment.author_id,
            content=comment.content,
        )
        self.db.add(m)
        await self.db.flush()
        await self.db.refresh(m)
        return comment_model_to_entity(m)

    async def get_by_id(self, comment_id: int) -> Comment | None:
        m = await self.db.get(CommentModel, comment_id)
        return comment_model_to_entity(m) if m else None

    async def get_by_post(
        self, post_id: int, limit: int, offset: int
    ) -> list[Comment]:
        r = await self.db.execute(
            select(CommentModel)
            .where(CommentModel.post_id == post_id)
            .order_by(CommentModel.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return [comment_model_to_entity(m) for m in r.scalars().all()]

    async def delete(self, comment_id: int) -> None:
        m = await self.db.get(CommentModel, comment_id)
        if m:
            await self.db.delete(m)
            await self.db.flush()


class SqlAlchemyLikeRepository(LikeRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, like: Like) -> Like:
        m = LikeModel(post_id=like.post_id, user_id=like.user_id)
        self.db.add(m)
        await self.db.flush()
        await self.db.refresh(m)
        return like_model_to_entity(m)

    async def get(self, post_id: int, user_id: int) -> Like | None:
        r = await self.db.execute(
            select(LikeModel).where(
                LikeModel.post_id == post_id, LikeModel.user_id == user_id
            )
        )
        m = r.scalar_one_or_none()
        return like_model_to_entity(m) if m else None

    async def delete(self, post_id: int, user_id: int) -> None:
        r = await self.db.execute(
            select(LikeModel).where(
                LikeModel.post_id == post_id, LikeModel.user_id == user_id
            )
        )
        m = r.scalar_one_or_none()
        if m:
            await self.db.delete(m)
            await self.db.flush()

    async def count_by_post(self, post_id: int) -> int:
        r = await self.db.execute(
            select(func.count())
            .select_from(LikeModel)
            .where(LikeModel.post_id == post_id)
        )
        return r.scalar_one()
