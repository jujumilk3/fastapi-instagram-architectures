from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from modular_monolith.modules.auth.models import User
from modular_monolith.modules.comment.models import Comment
from modular_monolith.modules.comment.schemas import CommentCreate, CommentResponse
from modular_monolith.modules.notification.service import NotificationService
from modular_monolith.modules.post.models import Post


class CommentService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, post_id: int, author_id: int, data: CommentCreate) -> CommentResponse:
        post = await self.db.get(Post, post_id)
        if not post:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

        comment = Comment(post_id=post_id, author_id=author_id, content=data.content)
        self.db.add(comment)
        await self.db.flush()
        await self.db.refresh(comment)

        if post.author_id != author_id:
            await NotificationService(self.db).create_notification(
                user_id=post.author_id, actor_id=author_id,
                type="comment", reference_id=post_id, message="commented on your post",
            )

        return CommentResponse(
            id=comment.id, post_id=comment.post_id, author_id=comment.author_id,
            content=comment.content, created_at=comment.created_at,
        )

    async def get_by_post(self, post_id: int, limit: int = 50, offset: int = 0) -> list[CommentResponse]:
        result = await self.db.execute(
            select(Comment).where(Comment.post_id == post_id).order_by(Comment.created_at.desc()).limit(limit).offset(offset)
        )
        responses = []
        for c in result.scalars().all():
            user = await self.db.get(User, c.author_id)
            responses.append(CommentResponse(
                id=c.id, post_id=c.post_id, author_id=c.author_id,
                author_username=user.username if user else None,
                content=c.content, created_at=c.created_at,
            ))
        return responses

    async def delete(self, comment_id: int, user_id: int) -> None:
        comment = await self.db.get(Comment, comment_id)
        if not comment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
        if comment.author_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your comment")
        await self.db.delete(comment)
        await self.db.flush()
