from fastapi import HTTPException, status

from clean.use_cases.interfaces.repositories import CommentRepository


class DeleteCommentUseCase:
    def __init__(self, comment_repo: CommentRepository):
        self.comment_repo = comment_repo

    async def execute(self, comment_id: int, user_id: int) -> None:
        comment = await self.comment_repo.get_by_id(comment_id)
        if not comment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
        if comment.author_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your comment")
        await self.comment_repo.delete(comment_id)
