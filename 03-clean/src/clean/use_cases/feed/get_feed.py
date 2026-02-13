from clean.use_cases.interfaces.repositories import CommentRepository, FollowRepository, LikeRepository, PostRepository, UserRepository
from clean.use_cases.post.create_post import _enrich_post


class GetFeedUseCase:
    def __init__(self, post_repo: PostRepository, follow_repo: FollowRepository,
                 user_repo: UserRepository, like_repo: LikeRepository,
                 comment_repo: CommentRepository):
        self.post_repo = post_repo
        self.follow_repo = follow_repo
        self.user_repo = user_repo
        self.like_repo = like_repo
        self.comment_repo = comment_repo

    async def execute(self, user_id: int, limit: int = 20, offset: int = 0) -> list[dict]:
        following_ids = await self.follow_repo.get_following(user_id)
        following_ids.append(user_id)
        posts = await self.post_repo.get_feed(following_ids, limit, offset)
        return [await _enrich_post(p, self.user_repo, self.like_repo, self.comment_repo) for p in posts]
