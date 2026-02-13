import re

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from layered.models.post import Post
from layered.repositories.hashtag import HashtagRepository
from layered.repositories.post import PostRepository
from layered.schemas.post import PostCreate, PostResponse


def extract_hashtags(text: str | None) -> list[str]:
    if not text:
        return []
    return re.findall(r"#(\w+)", text)


def _post_to_response(post: Post) -> PostResponse:
    return PostResponse(
        id=post.id,
        author_id=post.author_id,
        author_username=post.author.username if post.author else None,
        content=post.content,
        image_url=post.image_url,
        like_count=len(post.likes) if post.likes else 0,
        comment_count=len(post.comments) if post.comments else 0,
        created_at=post.created_at,
    )


class PostService:
    def __init__(self, db: AsyncSession):
        self.post_repo = PostRepository(db)
        self.hashtag_repo = HashtagRepository(db)

    async def create(self, author_id: int, data: PostCreate) -> PostResponse:
        post = Post(author_id=author_id, content=data.content, image_url=data.image_url)
        post = await self.post_repo.create(post)

        for tag in extract_hashtags(data.content):
            hashtag = await self.hashtag_repo.get_or_create(tag.lower())
            await self.hashtag_repo.link_post(post.id, hashtag.id)

        post = await self.post_repo.get_by_id(post.id)
        return _post_to_response(post)

    async def get(self, post_id: int) -> PostResponse:
        post = await self.post_repo.get_by_id(post_id)
        if not post:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
        return _post_to_response(post)

    async def get_by_author(self, author_id: int, limit: int = 20, offset: int = 0) -> list[PostResponse]:
        posts = await self.post_repo.get_by_author(author_id, limit, offset)
        return [_post_to_response(p) for p in posts]

    async def delete(self, post_id: int, user_id: int) -> None:
        post = await self.post_repo.get_by_id(post_id)
        if not post:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
        if post.author_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your post")
        await self.hashtag_repo.unlink_post(post_id)
        await self.post_repo.delete(post)
