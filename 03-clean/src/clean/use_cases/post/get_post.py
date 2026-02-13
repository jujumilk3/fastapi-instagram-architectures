from fastapi import HTTPException, status

from clean.use_cases.interfaces.repositories import CommentRepository, LikeRepository, PostRepository, UserRepository
from clean.use_cases.post.create_post import _enrich_post


class GetPostUseCase:
    def __init__(self, post_repo: PostRepository, user_repo: UserRepository,
                 like_repo: LikeRepository, comment_repo: CommentRepository):
        self.post_repo = post_repo
        self.user_repo = user_repo
        self.like_repo = like_repo
        self.comment_repo = comment_repo

    async def execute(self, post_id: int) -> dict:
        post = await self.post_repo.get_by_id(post_id)
        if not post:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
        return await _enrich_post(post, self.user_repo, self.like_repo, self.comment_repo)
