from fastapi import HTTPException, status
from sqlalchemy import select

from cqrs_es.read.projections.models import (
    FollowProjection,
    StoryProjection,
    UserProjection,
)
from cqrs_es.shared import event_bus
from cqrs_es.shared.event_store import append_event, get_next_version
from cqrs_es.write.aggregates.social import FollowAggregate, StoryAggregate
from cqrs_es.write.commands.commands import (
    CreateStory,
    DeleteStory,
    FollowUser,
    UnfollowUser,
)


async def handle_follow_user(cmd: FollowUser) -> dict:
    if cmd.follower_id == cmd.following_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot follow yourself")

    result = await cmd.db.execute(
        select(UserProjection).where(UserProjection.id == cmd.following_id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    existing = await cmd.db.execute(
        select(FollowProjection).where(
            FollowProjection.follower_id == cmd.follower_id,
            FollowProjection.following_id == cmd.following_id,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Already following")

    event_type, event_data = FollowAggregate.follow(cmd.follower_id, cmd.following_id)
    aggregate_id = f"{cmd.follower_id}"
    version = await get_next_version(cmd.db, "Follow", aggregate_id)
    await append_event(cmd.db, "Follow", aggregate_id, event_type, event_data, version)
    await event_bus.publish(event_type, event_data, db=cmd.db)

    return {"following": True}


async def handle_unfollow_user(cmd: UnfollowUser) -> dict:
    existing = await cmd.db.execute(
        select(FollowProjection).where(
            FollowProjection.follower_id == cmd.follower_id,
            FollowProjection.following_id == cmd.following_id,
        )
    )
    if not existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not following")

    event_type, event_data = FollowAggregate.unfollow(cmd.follower_id, cmd.following_id)
    aggregate_id = f"{cmd.follower_id}"
    version = await get_next_version(cmd.db, "Follow", aggregate_id)
    await append_event(cmd.db, "Follow", aggregate_id, event_type, event_data, version)
    await event_bus.publish(event_type, event_data, db=cmd.db)

    return {"following": False}


async def handle_create_story(cmd: CreateStory) -> dict:
    result = await cmd.db.execute(
        select(StoryProjection.id).order_by(StoryProjection.id.desc()).limit(1)
    )
    max_id = result.scalar_one_or_none() or 0
    story_id = max_id + 1

    event_type, event_data = StoryAggregate.create(
        story_id, cmd.author_id, cmd.image_url, cmd.content
    )
    version = await get_next_version(cmd.db, "Story", str(story_id))
    await append_event(cmd.db, "Story", str(story_id), event_type, event_data, version)
    await event_bus.publish(event_type, event_data, db=cmd.db)

    result = await cmd.db.execute(
        select(StoryProjection).where(StoryProjection.id == story_id)
    )
    story = result.scalar_one()
    return {
        "id": story.id, "author_id": story.author_id,
        "author_username": story.author_username,
        "image_url": story.image_url, "content": story.content,
        "created_at": story.created_at,
    }


async def handle_delete_story(cmd: DeleteStory) -> None:
    result = await cmd.db.execute(
        select(StoryProjection).where(StoryProjection.id == cmd.story_id)
    )
    story = result.scalar_one_or_none()
    if not story:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Story not found")
    if story.author_id != cmd.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your story")

    event_type, event_data = StoryAggregate.delete(cmd.story_id, story.author_id)
    version = await get_next_version(cmd.db, "Story", str(cmd.story_id))
    await append_event(cmd.db, "Story", str(cmd.story_id), event_type, event_data, version)
    await event_bus.publish(event_type, event_data, db=cmd.db)
