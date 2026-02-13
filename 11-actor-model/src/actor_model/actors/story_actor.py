from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from actor_model.actors.base import Actor, Message
from actor_model.actors.messages import (
    CreateStoryMessage,
    DeleteStoryMessage,
    GetStoriesMessage,
    GetStoryFeedMessage,
)
from actor_model.models.tables import Follow, Story

STORY_TTL_HOURS = 24


def _get_story_cutoff() -> datetime:
    return datetime.now(timezone.utc) - timedelta(hours=STORY_TTL_HOURS)


class StoryActor(Actor):
    async def receive(self, message: Message):
        match message:
            case CreateStoryMessage():
                await self._handle_create(message)
            case GetStoriesMessage():
                await self._handle_get_stories(message)
            case GetStoryFeedMessage():
                await self._handle_get_story_feed(message)
            case DeleteStoryMessage():
                await self._handle_delete(message)

    async def _handle_create(self, msg: CreateStoryMessage):
        async with msg.db_factory() as db:
            story = Story(author_id=msg.author_id, image_url=msg.image_url, content=msg.content)
            db.add(story)
            await db.flush()
            await db.refresh(story)

            result = {
                "id": story.id,
                "author_id": story.author_id,
                "image_url": story.image_url,
                "content": story.content,
                "created_at": story.created_at,
            }
            await db.commit()
            msg.reply(result)

    async def _handle_get_stories(self, msg: GetStoriesMessage):
        async with msg.db_factory() as db:
            cutoff = _get_story_cutoff()
            result = await db.execute(
                select(Story)
                .options(selectinload(Story.author))
                .where(Story.author_id == msg.user_id, Story.created_at >= cutoff)
                .order_by(Story.created_at.desc())
            )
            stories = [
                {
                    "id": s.id,
                    "author_id": s.author_id,
                    "author_username": s.author.username if s.author else None,
                    "image_url": s.image_url,
                    "content": s.content,
                    "created_at": s.created_at,
                }
                for s in result.scalars().all()
            ]
            msg.reply(stories)

    async def _handle_get_story_feed(self, msg: GetStoryFeedMessage):
        async with msg.db_factory() as db:
            following_result = await db.execute(
                select(Follow.following_id).where(Follow.follower_id == msg.user_id)
            )
            following_ids = list(following_result.scalars().all())
            following_ids.append(msg.user_id)

            cutoff = _get_story_cutoff()
            result = await db.execute(
                select(Story)
                .options(selectinload(Story.author))
                .where(Story.author_id.in_(following_ids), Story.created_at >= cutoff)
                .order_by(Story.created_at.desc())
            )
            stories = [
                {
                    "id": s.id,
                    "author_id": s.author_id,
                    "author_username": s.author.username if s.author else None,
                    "image_url": s.image_url,
                    "content": s.content,
                    "created_at": s.created_at,
                }
                for s in result.scalars().all()
            ]
            msg.reply(stories)

    async def _handle_delete(self, msg: DeleteStoryMessage):
        async with msg.db_factory() as db:
            story = await db.get(Story, msg.story_id)
            if not story:
                raise ValueError("Story not found")
            if story.author_id != msg.user_id:
                raise PermissionError("Not your story")

            await db.delete(story)
            await db.commit()
            msg.reply(None)
