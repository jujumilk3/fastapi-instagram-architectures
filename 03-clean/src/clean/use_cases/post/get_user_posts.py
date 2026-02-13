from clean.use_cases.interfaces.repositories import CommentRepository, LikeRepository, PostRepository, UserRepository
from clean.use_cases.post.create_post import _enrich_post


class GetUserPostsUseCase:
    def __init__(self, post_repo: PostRepository, user_repo: UserRepository,
                 like_repo: LikeRepository, comment_repo: CommentRepository):
        self.post_repo = post_repo
        self.user_repo = user_repo
        self.like_repo = like_repo
        self.comment_repo = comment_repo

    async def execute(self, author_id: int, limit: int = 20, offset: int = 0) -> list[dict]:
        posts = await self.post_repo.get_by_author(author_id, limit, offset)
        return [await _enrich_post(p, self.user_repo, self.like_repo, self.comment_repo) for p in posts]
