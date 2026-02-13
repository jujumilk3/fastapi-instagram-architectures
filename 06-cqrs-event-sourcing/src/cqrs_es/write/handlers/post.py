from fastapi import HTTPException, status
from sqlalchemy import select

from cqrs_es.read.projections.models import (
    CommentProjection,
    LikeProjection,
    PostProjection,
    UserProjection,
)
from cqrs_es.shared import event_bus
from cqrs_es.shared.event_store import append_event, get_next_version
from cqrs_es.write.aggregates.post import PostAggregate
from cqrs_es.write.commands.commands import (
    CreateComment,
    CreatePost,
    DeleteComment,
    DeletePost,
    ToggleLike,
)


async def handle_create_post(cmd: CreatePost) -> dict:
    result = await cmd.db.execute(
        select(PostProjection.id).order_by(PostProjection.id.desc()).limit(1)
    )
    max_id = result.scalar_one_or_none() or 0
    post_id = max_id + 1

    event_type, event_data = PostAggregate.create(
        post_id, cmd.author_id, cmd.content, cmd.image_url
    )

    version = await get_next_version(cmd.db, "Post", str(post_id))
    await append_event(cmd.db, "Post", str(post_id), event_type, event_data, version)
    await event_bus.publish(event_type, event_data, db=cmd.db)

    result = await cmd.db.execute(
        select(PostProjection).where(PostProjection.id == post_id)
    )
    post = result.scalar_one()
    return {
        "id": post.id, "author_id": post.author_id,
        "author_username": post.author_username,
        "content": post.content, "image_url": post.image_url,
        "like_count": post.like_count, "comment_count": post.comment_count,
        "created_at": post.created_at,
    }


async def handle_delete_post(cmd: DeletePost) -> None:
    result = await cmd.db.execute(
        select(PostProjection).where(PostProjection.id == cmd.post_id)
    )
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    if post.author_id != cmd.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your post")

    event_type, event_data = PostAggregate.delete(cmd.post_id, post.author_id)
    version = await get_next_version(cmd.db, "Post", str(cmd.post_id))
    await append_event(cmd.db, "Post", str(cmd.post_id), event_type, event_data, version)
    await event_bus.publish(event_type, event_data, db=cmd.db)


async def handle_toggle_like(cmd: ToggleLike) -> dict:
    result = await cmd.db.execute(
        select(PostProjection).where(PostProjection.id == cmd.post_id)
    )
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    existing = await cmd.db.execute(
        select(LikeProjection).where(
            LikeProjection.post_id == cmd.post_id,
            LikeProjection.user_id == cmd.user_id,
        )
    )
    like = existing.scalar_one_or_none()

    if like:
        event_type, event_data = PostAggregate.remove_like(cmd.post_id, cmd.user_id)
        version = await get_next_version(cmd.db, "Post", str(cmd.post_id))
        await append_event(cmd.db, "Post", str(cmd.post_id), event_type, event_data, version)
        await event_bus.publish(event_type, event_data, db=cmd.db)
        liked = False
    else:
        event_type, event_data = PostAggregate.add_like(
            cmd.post_id, cmd.user_id, post.author_id
        )
        version = await get_next_version(cmd.db, "Post", str(cmd.post_id))
        await append_event(cmd.db, "Post", str(cmd.post_id), event_type, event_data, version)
        await event_bus.publish(event_type, event_data, db=cmd.db)
        liked = True

    result = await cmd.db.execute(
        select(PostProjection).where(PostProjection.id == cmd.post_id)
    )
    post = result.scalar_one()
    return {"liked": liked, "like_count": post.like_count}


async def handle_create_comment(cmd: CreateComment) -> dict:
    result = await cmd.db.execute(
        select(PostProjection).where(PostProjection.id == cmd.post_id)
    )
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    cmt_result = await cmd.db.execute(
        select(CommentProjection.id).order_by(CommentProjection.id.desc()).limit(1)
    )
    max_id = cmt_result.scalar_one_or_none() or 0
    comment_id = max_id + 1

    event_type, event_data = PostAggregate.add_comment(
        comment_id, cmd.post_id, cmd.author_id, cmd.content, post.author_id
    )
    version = await get_next_version(cmd.db, "Post", str(cmd.post_id))
    await append_event(cmd.db, "Post", str(cmd.post_id), event_type, event_data, version)
    await event_bus.publish(event_type, event_data, db=cmd.db)

    result = await cmd.db.execute(
        select(CommentProjection).where(CommentProjection.id == comment_id)
    )
    comment = result.scalar_one()
    return {
        "id": comment.id, "post_id": comment.post_id,
        "author_id": comment.author_id,
        "author_username": comment.author_username,
        "content": comment.content, "created_at": comment.created_at,
    }


async def handle_delete_comment(cmd: DeleteComment) -> None:
    result = await cmd.db.execute(
        select(CommentProjection).where(CommentProjection.id == cmd.comment_id)
    )
    comment = result.scalar_one_or_none()
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    if comment.author_id != cmd.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your comment")

    event_type, event_data = PostAggregate.remove_comment(cmd.comment_id, comment.post_id)
    version = await get_next_version(cmd.db, "Post", str(comment.post_id))
    await append_event(cmd.db, "Post", str(comment.post_id), event_type, event_data, version)
    await event_bus.publish(event_type, event_data, db=cmd.db)
