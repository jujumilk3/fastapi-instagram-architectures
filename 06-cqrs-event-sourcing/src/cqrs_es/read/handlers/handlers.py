from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from cqrs_es.read.projections.models import (
    CommentProjection,
    FollowProjection,
    HashtagProjection,
    MessageProjection,
    NotificationProjection,
    PostHashtagProjection,
    PostProjection,
    StoryProjection,
    UserProjection,
)
from cqrs_es.read.queries.queries import (
    GetConversation,
    GetConversations,
    GetFeed,
    GetMyStories,
    GetNotifications,
    GetPost,
    GetPostComments,
    GetPostsByHashtag,
    GetStoryFeed,
    GetUserById,
    GetUserByEmail,
    GetUserFollowers,
    GetUserFollowing,
    GetUserPosts,
    GetUserProfile,
    SearchHashtags,
    SearchUsers,
)


async def handle_get_user_by_id(query: GetUserById) -> UserProjection | None:
    result = await query.db.execute(
        select(UserProjection).where(UserProjection.id == query.user_id)
    )
    return result.scalar_one_or_none()


async def handle_get_user_by_email(query: GetUserByEmail) -> UserProjection | None:
    result = await query.db.execute(
        select(UserProjection).where(UserProjection.email == query.email)
    )
    return result.scalar_one_or_none()


async def handle_get_user_profile(query: GetUserProfile) -> dict | None:
    result = await query.db.execute(
        select(UserProjection).where(UserProjection.id == query.user_id)
    )
    user = result.scalar_one_or_none()
    if not user:
        return None
    return {
        "id": user.id,
        "username": user.username,
        "full_name": user.full_name,
        "bio": user.bio,
        "profile_image_url": user.profile_image_url,
        "post_count": user.post_count,
        "follower_count": user.follower_count,
        "following_count": user.following_count,
    }


async def handle_get_user_posts(query: GetUserPosts) -> list[dict]:
    stmt = (
        select(PostProjection)
        .where(PostProjection.author_id == query.user_id)
        .order_by(PostProjection.created_at.desc())
        .limit(query.limit)
        .offset(query.offset)
    )
    result = await query.db.execute(stmt)
    return [_post_to_dict(p) for p in result.scalars().all()]


async def handle_get_user_followers(query: GetUserFollowers) -> list[dict]:
    stmt = select(FollowProjection.follower_id).where(
        FollowProjection.following_id == query.user_id
    )
    result = await query.db.execute(stmt)
    follower_ids = [row[0] for row in result.all()]
    if not follower_ids:
        return []
    users_result = await query.db.execute(
        select(UserProjection).where(UserProjection.id.in_(follower_ids))
    )
    return [_user_to_dict(u) for u in users_result.scalars().all()]


async def handle_get_user_following(query: GetUserFollowing) -> list[dict]:
    stmt = select(FollowProjection.following_id).where(
        FollowProjection.follower_id == query.user_id
    )
    result = await query.db.execute(stmt)
    following_ids = [row[0] for row in result.all()]
    if not following_ids:
        return []
    users_result = await query.db.execute(
        select(UserProjection).where(UserProjection.id.in_(following_ids))
    )
    return [_user_to_dict(u) for u in users_result.scalars().all()]


async def handle_get_post(query: GetPost) -> dict | None:
    result = await query.db.execute(
        select(PostProjection).where(PostProjection.id == query.post_id)
    )
    post = result.scalar_one_or_none()
    if not post:
        return None
    return _post_to_dict(post)


async def handle_get_post_comments(query: GetPostComments) -> list[dict]:
    stmt = (
        select(CommentProjection)
        .where(CommentProjection.post_id == query.post_id)
        .order_by(CommentProjection.created_at.desc())
    )
    if query.limit > 0:
        stmt = stmt.limit(query.limit).offset(query.offset)
    result = await query.db.execute(stmt)
    return [
        {
            "id": c.id,
            "post_id": c.post_id,
            "author_id": c.author_id,
            "author_username": c.author_username,
            "content": c.content,
            "created_at": c.created_at,
        }
        for c in result.scalars().all()
    ]


async def handle_get_feed(query: GetFeed) -> list[dict]:
    following_stmt = select(FollowProjection.following_id).where(
        FollowProjection.follower_id == query.user_id
    )
    result = await query.db.execute(following_stmt)
    following_ids = [row[0] for row in result.all()]
    following_ids.append(query.user_id)

    stmt = (
        select(PostProjection)
        .where(PostProjection.author_id.in_(following_ids))
        .order_by(PostProjection.created_at.desc())
        .limit(query.limit)
        .offset(query.offset)
    )
    result = await query.db.execute(stmt)
    return [_post_to_dict(p) for p in result.scalars().all()]


async def handle_get_my_stories(query: GetMyStories) -> list[dict]:
    stmt = (
        select(StoryProjection)
        .where(StoryProjection.author_id == query.user_id)
        .order_by(StoryProjection.created_at.desc())
    )
    result = await query.db.execute(stmt)
    return [_story_to_dict(s) for s in result.scalars().all()]


async def handle_get_story_feed(query: GetStoryFeed) -> list[dict]:
    following_stmt = select(FollowProjection.following_id).where(
        FollowProjection.follower_id == query.user_id
    )
    result = await query.db.execute(following_stmt)
    following_ids = [row[0] for row in result.all()]
    following_ids.append(query.user_id)

    stmt = (
        select(StoryProjection)
        .where(StoryProjection.author_id.in_(following_ids))
        .order_by(StoryProjection.created_at.desc())
    )
    result = await query.db.execute(stmt)
    return [_story_to_dict(s) for s in result.scalars().all()]


async def handle_get_conversations(query: GetConversations) -> list[dict]:
    stmt = (
        select(MessageProjection)
        .where(
            or_(
                MessageProjection.sender_id == query.user_id,
                MessageProjection.receiver_id == query.user_id,
            )
        )
        .order_by(MessageProjection.created_at.desc())
    )
    result = await query.db.execute(stmt)
    messages = result.scalars().all()

    conversations: dict[int, MessageProjection] = {}
    for msg in messages:
        other_id = msg.receiver_id if msg.sender_id == query.user_id else msg.sender_id
        if other_id not in conversations:
            conversations[other_id] = msg

    return [
        {
            "other_user_id": other_id,
            "last_message": {
                "id": msg.id,
                "sender_id": msg.sender_id,
                "receiver_id": msg.receiver_id,
                "content": msg.content,
                "is_read": msg.is_read,
                "created_at": msg.created_at,
            },
        }
        for other_id, msg in conversations.items()
    ]


async def handle_get_conversation(query: GetConversation) -> list[dict]:
    stmt = (
        select(MessageProjection)
        .where(
            or_(
                (MessageProjection.sender_id == query.user_id)
                & (MessageProjection.receiver_id == query.other_user_id),
                (MessageProjection.sender_id == query.other_user_id)
                & (MessageProjection.receiver_id == query.user_id),
            )
        )
        .order_by(MessageProjection.created_at.desc())
        .limit(query.limit)
        .offset(query.offset)
    )
    result = await query.db.execute(stmt)
    return [
        {
            "id": m.id,
            "sender_id": m.sender_id,
            "receiver_id": m.receiver_id,
            "content": m.content,
            "is_read": m.is_read,
            "created_at": m.created_at,
        }
        for m in result.scalars().all()
    ]


async def handle_get_notifications(query: GetNotifications) -> list[dict]:
    stmt = (
        select(NotificationProjection)
        .where(NotificationProjection.user_id == query.user_id)
        .order_by(NotificationProjection.created_at.desc())
        .limit(query.limit)
        .offset(query.offset)
    )
    result = await query.db.execute(stmt)
    return [
        {
            "id": n.id,
            "user_id": n.user_id,
            "actor_id": n.actor_id,
            "type": n.type,
            "reference_id": n.reference_id,
            "message": n.message,
            "is_read": n.is_read,
            "created_at": n.created_at,
        }
        for n in result.scalars().all()
    ]


async def handle_search_users(query: SearchUsers) -> list[dict]:
    stmt = (
        select(UserProjection)
        .where(UserProjection.username.ilike(f"%{query.query}%"))
        .limit(query.limit)
    )
    result = await query.db.execute(stmt)
    return [_user_to_dict(u) for u in result.scalars().all()]


async def handle_search_hashtags(query: SearchHashtags) -> list[dict]:
    stmt = (
        select(HashtagProjection)
        .where(HashtagProjection.name.ilike(f"%{query.query}%"))
        .limit(query.limit)
    )
    result = await query.db.execute(stmt)
    return [{"id": h.id, "name": h.name} for h in result.scalars().all()]


async def handle_get_posts_by_hashtag(query: GetPostsByHashtag) -> list[dict]:
    tag_result = await query.db.execute(
        select(HashtagProjection).where(HashtagProjection.name == query.tag.lower())
    )
    hashtag = tag_result.scalar_one_or_none()
    if not hashtag:
        return []

    stmt = (
        select(PostProjection)
        .join(PostHashtagProjection, PostHashtagProjection.post_id == PostProjection.id)
        .where(PostHashtagProjection.hashtag_id == hashtag.id)
        .order_by(PostProjection.created_at.desc())
        .limit(query.limit)
        .offset(query.offset)
    )
    result = await query.db.execute(stmt)
    return [_post_to_dict(p) for p in result.scalars().all()]


def _user_to_dict(u: UserProjection) -> dict:
    return {
        "id": u.id,
        "username": u.username,
        "email": u.email,
        "full_name": u.full_name,
        "bio": u.bio,
        "profile_image_url": u.profile_image_url,
        "is_active": u.is_active,
        "created_at": u.created_at,
    }


def _post_to_dict(p: PostProjection) -> dict:
    return {
        "id": p.id,
        "author_id": p.author_id,
        "author_username": p.author_username,
        "content": p.content,
        "image_url": p.image_url,
        "like_count": p.like_count,
        "comment_count": p.comment_count,
        "created_at": p.created_at,
    }


def _story_to_dict(s: StoryProjection) -> dict:
    return {
        "id": s.id,
        "author_id": s.author_id,
        "author_username": s.author_username,
        "image_url": s.image_url,
        "content": s.content,
        "created_at": s.created_at,
    }
