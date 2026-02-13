from __future__ import annotations

from fastapi import HTTPException, status

from ddd.domain.hashtag.repository import HashtagRepository
from ddd.domain.notification.entity import Notification
from ddd.domain.notification.repository import NotificationRepository
from ddd.domain.post.aggregate import PostAggregate
from ddd.domain.post.entities import Comment, Like
from ddd.domain.post.repository import CommentRepository, LikeRepository, PostRepository
from ddd.domain.shared.event import CommentAddedEvent, PostLikedEvent
from ddd.domain.user.repository import UserRepository


class PostApplicationService:
    def __init__(
        self,
        post_repo: PostRepository,
        user_repo: UserRepository,
        like_repo: LikeRepository,
        comment_repo: CommentRepository,
        hashtag_repo: HashtagRepository | None,
    ):
        self.post_repo = post_repo
        self.user_repo = user_repo
        self.like_repo = like_repo
        self.comment_repo = comment_repo
        self.hashtag_repo = hashtag_repo

    async def _enrich(self, post: PostAggregate) -> dict:
        author = await self.user_repo.get_by_id(post.author_id)
        like_count = await self.like_repo.count_by_post(post.id)
        comments = await self.comment_repo.get_by_post(post.id, 0, 0)
        return {
            "id": post.id,
            "author_id": post.author_id,
            "author_username": author.username.value if author else None,
            "content": post.content,
            "image_url": post.image_url,
            "like_count": like_count,
            "comment_count": len(comments),
            "created_at": post.created_at,
        }

    async def create(
        self,
        author_id: int,
        content: str | None = None,
        image_url: str | None = None,
    ) -> dict:
        post = PostAggregate.create(
            author_id=author_id, content=content, image_url=image_url
        )
        saved = await self.post_repo.create(post)
        if self.hashtag_repo and content:
            for tag in saved.extract_hashtags():
                h = await self.hashtag_repo.get_or_create(tag)
                await self.hashtag_repo.link_post(saved.id, h.id)
        saved.collect_events()
        return await self._enrich(saved)

    async def get(self, post_id: int) -> dict:
        post = await self.post_repo.get_by_id(post_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
            )
        return await self._enrich(post)

    async def get_by_author(
        self, author_id: int, limit: int = 20, offset: int = 0
    ) -> list[dict]:
        posts = await self.post_repo.get_by_author(author_id, limit, offset)
        return [await self._enrich(p) for p in posts]

    async def delete(self, post_id: int, user_id: int) -> None:
        post = await self.post_repo.get_by_id(post_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
            )
        if post.author_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Not your post"
            )
        if self.hashtag_repo:
            await self.hashtag_repo.unlink_post(post_id)
        await self.post_repo.delete(post_id)


class CommentApplicationService:
    def __init__(
        self,
        comment_repo: CommentRepository,
        post_repo: PostRepository,
        user_repo: UserRepository,
        notification_repo: NotificationRepository,
    ):
        self.comment_repo = comment_repo
        self.post_repo = post_repo
        self.user_repo = user_repo
        self.notification_repo = notification_repo

    async def create(self, post_id: int, author_id: int, content: str) -> dict:
        post = await self.post_repo.get_by_id(post_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
            )
        comment_entity = post.add_comment(author_id, content)
        saved = await self.comment_repo.create(comment_entity)

        events = post.collect_events()
        for event in events:
            if isinstance(event, CommentAddedEvent):
                await self.notification_repo.create(Notification(
                    user_id=event.post_author_id,
                    actor_id=event.author_id,
                    type="comment",
                    reference_id=event.post_id,
                    message="commented on your post",
                ))

        return {
            "id": saved.id,
            "post_id": saved.post_id,
            "author_id": saved.author_id,
            "content": saved.content,
            "created_at": saved.created_at,
        }

    async def get_by_post(
        self, post_id: int, limit: int = 50, offset: int = 0
    ) -> list[dict]:
        comments = await self.comment_repo.get_by_post(post_id, limit, offset)
        result = []
        for c in comments:
            author = await self.user_repo.get_by_id(c.author_id)
            result.append({
                "id": c.id,
                "post_id": c.post_id,
                "author_id": c.author_id,
                "author_username": author.username.value if author else None,
                "content": c.content,
                "created_at": c.created_at,
            })
        return result

    async def delete(self, comment_id: int, user_id: int) -> None:
        comment = await self.comment_repo.get_by_id(comment_id)
        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found"
            )
        if comment.author_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Not your comment"
            )
        await self.comment_repo.delete(comment_id)


class LikeApplicationService:
    def __init__(
        self,
        like_repo: LikeRepository,
        post_repo: PostRepository,
        notification_repo: NotificationRepository,
    ):
        self.like_repo = like_repo
        self.post_repo = post_repo
        self.notification_repo = notification_repo

    async def toggle(self, post_id: int, user_id: int) -> dict:
        post = await self.post_repo.get_by_id(post_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
            )
        existing = await self.like_repo.get(post_id, user_id)
        liked = post.toggle_like(user_id, already_liked=existing is not None)

        if liked:
            await self.like_repo.create(Like(post_id=post_id, user_id=user_id))
        else:
            await self.like_repo.delete(post_id, user_id)

        events = post.collect_events()
        for event in events:
            if isinstance(event, PostLikedEvent) and event.author_id != user_id:
                await self.notification_repo.create(Notification(
                    user_id=event.author_id,
                    actor_id=user_id,
                    type="like",
                    reference_id=post_id,
                    message="liked your post",
                ))

        count = await self.like_repo.count_by_post(post_id)
        return {"liked": liked, "like_count": count}
