import re

from clean.entities.post import Post
from clean.use_cases.interfaces.repositories import (
    CommentRepository,
    HashtagRepository,
    LikeRepository,
    PostRepository,
    UserRepository,
)


class CreatePostUseCase:
    def __init__(
        self,
        post_repo: PostRepository,
        user_repo: UserRepository,
        like_repo: LikeRepository,
        comment_repo: CommentRepository,
        hashtag_repo: HashtagRepository,
    ):
        self.post_repo = post_repo
        self.user_repo = user_repo
        self.like_repo = like_repo
        self.comment_repo = comment_repo
        self.hashtag_repo = hashtag_repo

    async def execute(self, author_id: int, content: str | None = None, image_url: str | None = None) -> dict:
        post = await self.post_repo.create(Post(author_id=author_id, content=content, image_url=image_url))
        if content:
            for tag in re.findall(r"#(\w+)", content):
                h = await self.hashtag_repo.get_or_create(tag.lower())
                await self.hashtag_repo.link_post(post.id, h.id)
        return await _enrich_post(post, self.user_repo, self.like_repo, self.comment_repo)


async def _enrich_post(post: Post, user_repo: UserRepository, like_repo: LikeRepository, comment_repo: CommentRepository) -> dict:
    author = await user_repo.get_by_id(post.author_id)
    like_count = await like_repo.count_by_post(post.id)
    comments = await comment_repo.get_by_post(post.id, 0, 0)
    return {
        "id": post.id,
        "author_id": post.author_id,
        "author_username": author.username if author else None,
        "content": post.content,
        "image_url": post.image_url,
        "like_count": like_count,
        "comment_count": len(comments),
        "created_at": post.created_at,
    }
