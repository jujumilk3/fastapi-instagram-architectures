import re
from datetime import datetime, timezone

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from cqrs_es.read.projections.models import (
    CommentProjection,
    FollowProjection,
    HashtagProjection,
    LikeProjection,
    MessageProjection,
    NotificationProjection,
    PostHashtagProjection,
    PostProjection,
    StoryProjection,
    UserProjection,
)


async def on_user_registered(event_data: dict, db: AsyncSession, **_) -> None:
    created_at = datetime.fromisoformat(event_data["created_at"]) if event_data.get("created_at") else datetime.now(timezone.utc)
    user = UserProjection(
        id=event_data["user_id"],
        username=event_data["username"],
        email=event_data["email"],
        hashed_password=event_data["hashed_password"],
        full_name=event_data.get("full_name"),
        is_active=True,
        post_count=0,
        follower_count=0,
        following_count=0,
        created_at=created_at,
    )
    db.add(user)
    await db.flush()


async def on_user_updated(event_data: dict, db: AsyncSession, **_) -> None:
    user_id = event_data["user_id"]
    values = {}
    for field in ("full_name", "bio", "profile_image_url"):
        if field in event_data:
            values[field] = event_data[field]
    if values:
        await db.execute(
            update(UserProjection).where(UserProjection.id == user_id).values(**values)
        )


async def on_post_created(event_data: dict, db: AsyncSession, **_) -> None:
    result = await db.execute(
        select(UserProjection.username).where(UserProjection.id == event_data["author_id"])
    )
    author_username = result.scalar_one_or_none()

    created_at = datetime.fromisoformat(event_data["created_at"]) if event_data.get("created_at") else datetime.now(timezone.utc)
    post = PostProjection(
        id=event_data["post_id"],
        author_id=event_data["author_id"],
        author_username=author_username,
        content=event_data.get("content"),
        image_url=event_data.get("image_url"),
        like_count=0,
        comment_count=0,
        created_at=created_at,
    )
    db.add(post)
    await db.flush()

    await db.execute(
        update(UserProjection)
        .where(UserProjection.id == event_data["author_id"])
        .values(post_count=UserProjection.post_count + 1)
    )

    content = event_data.get("content") or ""
    for tag in re.findall(r"#(\w+)", content):
        tag_lower = tag.lower()
        result = await db.execute(
            select(HashtagProjection).where(HashtagProjection.name == tag_lower)
        )
        hashtag = result.scalar_one_or_none()
        if not hashtag:
            hashtag = HashtagProjection(name=tag_lower)
            db.add(hashtag)
            await db.flush()
        link = PostHashtagProjection(
            post_id=event_data["post_id"], hashtag_id=hashtag.id
        )
        db.add(link)
        await db.flush()


async def on_post_deleted(event_data: dict, db: AsyncSession, **_) -> None:
    post_id = event_data["post_id"]

    await db.execute(delete(PostHashtagProjection).where(PostHashtagProjection.post_id == post_id))
    await db.execute(delete(CommentProjection).where(CommentProjection.post_id == post_id))
    await db.execute(delete(LikeProjection).where(LikeProjection.post_id == post_id))
    await db.execute(delete(PostProjection).where(PostProjection.id == post_id))

    await db.execute(
        update(UserProjection)
        .where(UserProjection.id == event_data["author_id"])
        .values(post_count=UserProjection.post_count - 1)
    )


async def on_like_added(event_data: dict, db: AsyncSession, **_) -> None:
    like = LikeProjection(post_id=event_data["post_id"], user_id=event_data["user_id"])
    db.add(like)
    await db.flush()
    await db.execute(
        update(PostProjection)
        .where(PostProjection.id == event_data["post_id"])
        .values(like_count=PostProjection.like_count + 1)
    )

    if event_data.get("post_author_id") and event_data["post_author_id"] != event_data["user_id"]:
        notification = NotificationProjection(
            user_id=event_data["post_author_id"],
            actor_id=event_data["user_id"],
            type="like",
            reference_id=event_data["post_id"],
            message="liked your post",
        )
        db.add(notification)
        await db.flush()


async def on_like_removed(event_data: dict, db: AsyncSession, **_) -> None:
    await db.execute(
        delete(LikeProjection).where(
            LikeProjection.post_id == event_data["post_id"],
            LikeProjection.user_id == event_data["user_id"],
        )
    )
    await db.execute(
        update(PostProjection)
        .where(PostProjection.id == event_data["post_id"])
        .values(like_count=PostProjection.like_count - 1)
    )


async def on_comment_created(event_data: dict, db: AsyncSession, **_) -> None:
    result = await db.execute(
        select(UserProjection.username).where(UserProjection.id == event_data["author_id"])
    )
    author_username = result.scalar_one_or_none()

    created_at = datetime.fromisoformat(event_data["created_at"]) if event_data.get("created_at") else datetime.now(timezone.utc)
    comment = CommentProjection(
        id=event_data["comment_id"],
        post_id=event_data["post_id"],
        author_id=event_data["author_id"],
        author_username=author_username,
        content=event_data["content"],
        created_at=created_at,
    )
    db.add(comment)
    await db.flush()

    await db.execute(
        update(PostProjection)
        .where(PostProjection.id == event_data["post_id"])
        .values(comment_count=PostProjection.comment_count + 1)
    )

    if event_data.get("post_author_id") and event_data["post_author_id"] != event_data["author_id"]:
        notification = NotificationProjection(
            user_id=event_data["post_author_id"],
            actor_id=event_data["author_id"],
            type="comment",
            reference_id=event_data["post_id"],
            message="commented on your post",
        )
        db.add(notification)
        await db.flush()


async def on_comment_deleted(event_data: dict, db: AsyncSession, **_) -> None:
    await db.execute(
        delete(CommentProjection).where(CommentProjection.id == event_data["comment_id"])
    )
    await db.execute(
        update(PostProjection)
        .where(PostProjection.id == event_data["post_id"])
        .values(comment_count=PostProjection.comment_count - 1)
    )


async def on_user_followed(event_data: dict, db: AsyncSession, **_) -> None:
    follow = FollowProjection(
        follower_id=event_data["follower_id"],
        following_id=event_data["following_id"],
    )
    db.add(follow)
    await db.flush()

    await db.execute(
        update(UserProjection)
        .where(UserProjection.id == event_data["follower_id"])
        .values(following_count=UserProjection.following_count + 1)
    )
    await db.execute(
        update(UserProjection)
        .where(UserProjection.id == event_data["following_id"])
        .values(follower_count=UserProjection.follower_count + 1)
    )

    notification = NotificationProjection(
        user_id=event_data["following_id"],
        actor_id=event_data["follower_id"],
        type="follow",
        message="started following you",
    )
    db.add(notification)
    await db.flush()


async def on_user_unfollowed(event_data: dict, db: AsyncSession, **_) -> None:
    await db.execute(
        delete(FollowProjection).where(
            FollowProjection.follower_id == event_data["follower_id"],
            FollowProjection.following_id == event_data["following_id"],
        )
    )
    await db.execute(
        update(UserProjection)
        .where(UserProjection.id == event_data["follower_id"])
        .values(following_count=UserProjection.following_count - 1)
    )
    await db.execute(
        update(UserProjection)
        .where(UserProjection.id == event_data["following_id"])
        .values(follower_count=UserProjection.follower_count - 1)
    )


async def on_story_created(event_data: dict, db: AsyncSession, **_) -> None:
    result = await db.execute(
        select(UserProjection.username).where(UserProjection.id == event_data["author_id"])
    )
    author_username = result.scalar_one_or_none()

    created_at = datetime.fromisoformat(event_data["created_at"]) if event_data.get("created_at") else datetime.now(timezone.utc)
    story = StoryProjection(
        id=event_data["story_id"],
        author_id=event_data["author_id"],
        author_username=author_username,
        image_url=event_data.get("image_url"),
        content=event_data.get("content"),
        created_at=created_at,
    )
    db.add(story)
    await db.flush()


async def on_story_deleted(event_data: dict, db: AsyncSession, **_) -> None:
    await db.execute(
        delete(StoryProjection).where(StoryProjection.id == event_data["story_id"])
    )


async def on_message_sent(event_data: dict, db: AsyncSession, **_) -> None:
    created_at = datetime.fromisoformat(event_data["created_at"]) if event_data.get("created_at") else datetime.now(timezone.utc)
    msg = MessageProjection(
        id=event_data["message_id"],
        sender_id=event_data["sender_id"],
        receiver_id=event_data["receiver_id"],
        content=event_data["content"],
        is_read=False,
        created_at=created_at,
    )
    db.add(msg)
    await db.flush()


async def on_messages_marked_read(event_data: dict, db: AsyncSession, **_) -> None:
    await db.execute(
        update(MessageProjection)
        .where(
            MessageProjection.sender_id == event_data["sender_id"],
            MessageProjection.receiver_id == event_data["user_id"],
            MessageProjection.is_read == False,  # noqa: E712
        )
        .values(is_read=True)
    )


async def on_notification_read(event_data: dict, db: AsyncSession, **_) -> None:
    await db.execute(
        update(NotificationProjection)
        .where(
            NotificationProjection.id == event_data["notification_id"],
            NotificationProjection.user_id == event_data["user_id"],
        )
        .values(is_read=True)
    )


async def on_all_notifications_read(event_data: dict, db: AsyncSession, **_) -> None:
    await db.execute(
        update(NotificationProjection)
        .where(
            NotificationProjection.user_id == event_data["user_id"],
            NotificationProjection.is_read == False,  # noqa: E712
        )
        .values(is_read=True)
    )
