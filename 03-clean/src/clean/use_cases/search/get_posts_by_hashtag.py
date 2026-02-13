from clean.use_cases.interfaces.repositories import CommentRepository, HashtagRepository, LikeRepository, UserRepository


class GetPostsByHashtagUseCase:
    def __init__(self, hashtag_repo: HashtagRepository, user_repo: UserRepository,
                 like_repo: LikeRepository, comment_repo: CommentRepository):
        self.hashtag_repo = hashtag_repo
        self.user_repo = user_repo
        self.like_repo = like_repo
        self.comment_repo = comment_repo

    async def execute(self, tag: str, limit: int = 20, offset: int = 0) -> list[dict]:
        posts = await self.hashtag_repo.get_posts_by_hashtag(tag, limit, offset)
        result = []
        for p in posts:
            author = await self.user_repo.get_by_id(p.author_id)
            like_count = await self.like_repo.count_by_post(p.id)
            comments = await self.comment_repo.get_by_post(p.id, 0, 0)
            result.append({
                "id": p.id, "author_id": p.author_id,
                "author_username": author.username if author else None,
                "content": p.content, "image_url": p.image_url,
                "like_count": like_count, "comment_count": len(comments),
                "created_at": p.created_at,
            })
        return result
