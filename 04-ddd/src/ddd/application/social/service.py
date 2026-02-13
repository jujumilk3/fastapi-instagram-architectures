from __future__ import annotations

from fastapi import HTTPException, status

from ddd.domain.notification.entity import Notification
from ddd.domain.notification.repository import NotificationRepository
from ddd.domain.social.aggregate import Follow, Story
from ddd.domain.social.repository import FollowRepository, StoryRepository
from ddd.domain.user.repository import UserRepository


class FollowApplicationService:
    def __init__(
        self,
        follow_repo: FollowRepository,
        user_repo: UserRepository,
        notification_repo: NotificationRepository,
    ):
        self.follow_repo = follow_repo
        self.user_repo = user_repo
        self.notification_repo = notification_repo

    async def follow(self, follower_id: int, following_id: int) -> dict:
        if follower_id == following_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot follow yourself",
            )
        if not await self.user_repo.get_by_id(following_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        if await self.follow_repo.get(follower_id, following_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Already following"
            )
        await self.follow_repo.create(
            Follow(follower_id=follower_id, following_id=following_id)
        )
        await self.notification_repo.create(Notification(
            user_id=following_id,
            actor_id=follower_id,
            type="follow",
            message="started following you",
        ))
        return {"following": True}

    async def unfollow(self, follower_id: int, following_id: int) -> dict:
        if not await self.follow_repo.get(follower_id, following_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Not following"
            )
        await self.follow_repo.delete(follower_id, following_id)
        return {"following": False}


class StoryApplicationService:
    def __init__(
        self,
        story_repo: StoryRepository,
        follow_repo: FollowRepository,
        user_repo: UserRepository,
    ):
        self.story_repo = story_repo
        self.follow_repo = follow_repo
        self.user_repo = user_repo

    async def _enrich(self, story: Story) -> dict:
        author = await self.user_repo.get_by_id(story.author_id)
        return {
            "id": story.id,
            "author_id": story.author_id,
            "author_username": author.username.value if author else None,
            "image_url": story.image_url,
            "content": story.content,
            "created_at": story.created_at,
        }

    async def create(
        self, author_id: int, image_url: str | None, content: str | None
    ) -> dict:
        story = await self.story_repo.create(
            Story(author_id=author_id, image_url=image_url, content=content)
        )
        return {
            "id": story.id,
            "author_id": story.author_id,
            "image_url": story.image_url,
            "content": story.content,
            "created_at": story.created_at,
        }

    async def get_my_stories(self, user_id: int) -> list[dict]:
        stories = await self.story_repo.get_active_by_author(user_id)
        return [await self._enrich(s) for s in stories]

    async def get_feed(self, user_id: int) -> list[dict]:
        ids = await self.follow_repo.get_following(user_id)
        ids.append(user_id)
        stories = await self.story_repo.get_feed(ids)
        return [await self._enrich(s) for s in stories]

    async def delete(self, story_id: int, user_id: int) -> None:
        story = await self.story_repo.get_by_id(story_id)
        if not story:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Story not found"
            )
        if story.author_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Not your story"
            )
        await self.story_repo.delete(story_id)
