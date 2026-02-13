from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from layered.models.comment import Comment
from layered.models.notification import Notification
from layered.repositories.comment import CommentRepository
from layered.repositories.notification import NotificationRepository
from layered.repositories.post import PostRepository
from layered.schemas.comment import CommentCreate, CommentResponse


class CommentService:
    def __init__(self, db: AsyncSession):
        self.comment_repo = CommentRepository(db)
        self.post_repo = PostRepository(db)
        self.notification_repo = NotificationRepository(db)

    async def create(self, post_id: int, author_id: int, data: CommentCreate) -> CommentResponse:
        post = await self.post_repo.get_by_id(post_id)
        if not post:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

        comment = Comment(post_id=post_id, author_id=author_id, content=data.content)
        comment = await self.comment_repo.create(comment)

        if post.author_id != author_id:
            await self.notification_repo.create(
                Notification(
                    user_id=post.author_id,
                    actor_id=author_id,
                    type="comment",
                    reference_id=post_id,
                    message=f"commented on your post",
                )
            )

        return CommentResponse(
            id=comment.id,
            post_id=comment.post_id,
            author_id=comment.author_id,
            content=comment.content,
            created_at=comment.created_at,
        )

    async def get_by_post(self, post_id: int, limit: int = 50, offset: int = 0) -> list[CommentResponse]:
        comments = await self.comment_repo.get_by_post(post_id, limit, offset)
        return [
            CommentResponse(
                id=c.id,
                post_id=c.post_id,
                author_id=c.author_id,
                author_username=c.author.username if c.author else None,
                content=c.content,
                created_at=c.created_at,
            )
            for c in comments
        ]

    async def delete(self, comment_id: int, user_id: int) -> None:
        comment = await self.comment_repo.get_by_id(comment_id)
        if not comment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
        if comment.author_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your comment")
        await self.comment_repo.delete(comment)
