from fastapi import HTTPException, status

from clean.entities.post import Comment
from clean.entities.social import Notification
from clean.use_cases.interfaces.repositories import CommentRepository, NotificationRepository, PostRepository, UserRepository


class CreateCommentUseCase:
    def __init__(self, comment_repo: CommentRepository, post_repo: PostRepository,
                 user_repo: UserRepository, notification_repo: NotificationRepository):
        self.comment_repo = comment_repo
        self.post_repo = post_repo
        self.user_repo = user_repo
        self.notification_repo = notification_repo

    async def execute(self, post_id: int, author_id: int, content: str) -> dict:
        post = await self.post_repo.get_by_id(post_id)
        if not post:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
        comment = await self.comment_repo.create(Comment(post_id=post_id, author_id=author_id, content=content))
        if post.author_id != author_id:
            await self.notification_repo.create(Notification(
                user_id=post.author_id, actor_id=author_id, type="comment",
                reference_id=post_id, message="commented on your post",
            ))
        return {
            "id": comment.id, "post_id": comment.post_id, "author_id": comment.author_id,
            "content": comment.content, "created_at": comment.created_at,
        }
