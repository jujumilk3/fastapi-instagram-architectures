import re

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from modular_monolith.modules.auth.models import User
from modular_monolith.modules.comment.models import Comment
from modular_monolith.modules.like.models import Like
from modular_monolith.modules.post.models import Hashtag, Post, PostHashtag
from modular_monolith.modules.post.schemas import PostCreate, PostResponse


def extract_hashtags(text: str | None) -> list[str]:
    if not text:
        return []
    return re.findall(r"#(\w+)", text)


class PostService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def _to_response(self, post: Post) -> PostResponse:
        user = await self.db.get(User, post.author_id)
        like_count = (await self.db.execute(
            select(func.count()).select_from(Like).where(Like.post_id == post.id)
        )).scalar_one()
        comment_count = (await self.db.execute(
            select(func.count()).select_from(Comment).where(Comment.post_id == post.id)
        )).scalar_one()
        return PostResponse(
            id=post.id, author_id=post.author_id,
            author_username=user.username if user else None,
            content=post.content, image_url=post.image_url,
            like_count=like_count, comment_count=comment_count,
            created_at=post.created_at,
        )

    async def _process_hashtags(self, post_id: int, content: str | None):
        for tag in extract_hashtags(content):
            tag_lower = tag.lower()
            result = await self.db.execute(select(Hashtag).where(Hashtag.name == tag_lower))
            hashtag = result.scalar_one_or_none()
            if not hashtag:
                hashtag = Hashtag(name=tag_lower)
                self.db.add(hashtag)
                await self.db.flush()
                await self.db.refresh(hashtag)
            self.db.add(PostHashtag(post_id=post_id, hashtag_id=hashtag.id))
        await self.db.flush()

    async def create(self, author_id: int, data: PostCreate) -> PostResponse:
        post = Post(author_id=author_id, content=data.content, image_url=data.image_url)
        self.db.add(post)
        await self.db.flush()
        await self.db.refresh(post)
        await self._process_hashtags(post.id, data.content)
        return await self._to_response(post)

    async def get(self, post_id: int) -> PostResponse:
        post = await self.db.get(Post, post_id)
        if not post:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
        return await self._to_response(post)

    async def get_by_author(self, author_id: int, limit: int = 20, offset: int = 0) -> list[PostResponse]:
        result = await self.db.execute(
            select(Post).where(Post.author_id == author_id).order_by(Post.created_at.desc()).limit(limit).offset(offset)
        )
        return [await self._to_response(p) for p in result.scalars().all()]

    async def delete(self, post_id: int, user_id: int) -> None:
        post = await self.db.get(Post, post_id)
        if not post:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
        if post.author_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your post")
        # Clean up hashtag links
        result = await self.db.execute(select(PostHashtag).where(PostHashtag.post_id == post_id))
        for ph in result.scalars().all():
            await self.db.delete(ph)
        await self.db.delete(post)
        await self.db.flush()
