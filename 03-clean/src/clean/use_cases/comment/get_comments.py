from clean.use_cases.interfaces.repositories import CommentRepository, UserRepository


class GetCommentsUseCase:
    def __init__(self, comment_repo: CommentRepository, user_repo: UserRepository):
        self.comment_repo = comment_repo
        self.user_repo = user_repo

    async def execute(self, post_id: int, limit: int = 50, offset: int = 0) -> list[dict]:
        comments = await self.comment_repo.get_by_post(post_id, limit, offset)
        result = []
        for c in comments:
            author = await self.user_repo.get_by_id(c.author_id)
            result.append({
                "id": c.id, "post_id": c.post_id, "author_id": c.author_id,
                "author_username": author.username if author else None,
                "content": c.content, "created_at": c.created_at,
            })
        return result
