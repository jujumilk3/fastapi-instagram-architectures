from __future__ import annotations

from ddd.domain.hashtag.entity import Hashtag
from ddd.domain.messaging.aggregate import Message
from ddd.domain.notification.entity import Notification
from ddd.domain.post.aggregate import PostAggregate
from ddd.domain.post.entities import Comment, Like
from ddd.domain.social.aggregate import Follow, Story
from ddd.domain.user.aggregate import UserAggregate
from ddd.infrastructure.orm.models import (
    CommentModel,
    FollowModel,
    HashtagModel,
    LikeModel,
    MessageModel,
    NotificationModel,
    PostModel,
    StoryModel,
    UserModel,
)


def user_model_to_aggregate(m: UserModel) -> UserAggregate:
    return UserAggregate.reconstitute(
        id=m.id,
        username=m.username,
        email=m.email,
        hashed_password=m.hashed_password,
        full_name=m.full_name,
        bio=m.bio,
        profile_image_url=m.profile_image_url,
        is_active=m.is_active,
        created_at=m.created_at,
        updated_at=m.updated_at,
    )


def post_model_to_aggregate(m: PostModel) -> PostAggregate:
    return PostAggregate.reconstitute(
        id=m.id,
        author_id=m.author_id,
        content=m.content,
        image_url=m.image_url,
        created_at=m.created_at,
        updated_at=m.updated_at,
    )


def comment_model_to_entity(m: CommentModel) -> Comment:
    return Comment(
        id=m.id,
        post_id=m.post_id,
        author_id=m.author_id,
        content=m.content,
        created_at=m.created_at,
    )


def like_model_to_entity(m: LikeModel) -> Like:
    return Like(
        id=m.id, post_id=m.post_id, user_id=m.user_id, created_at=m.created_at
    )


def follow_model_to_entity(m: FollowModel) -> Follow:
    return Follow(
        id=m.id,
        follower_id=m.follower_id,
        following_id=m.following_id,
        created_at=m.created_at,
    )


def story_model_to_entity(m: StoryModel) -> Story:
    return Story(
        id=m.id,
        author_id=m.author_id,
        image_url=m.image_url,
        content=m.content,
        created_at=m.created_at,
    )


def message_model_to_entity(m: MessageModel) -> Message:
    return Message(
        id=m.id,
        sender_id=m.sender_id,
        receiver_id=m.receiver_id,
        content=m.content,
        is_read=m.is_read,
        created_at=m.created_at,
    )


def notification_model_to_entity(m: NotificationModel) -> Notification:
    return Notification(
        id=m.id,
        user_id=m.user_id,
        actor_id=m.actor_id,
        type=m.type,
        reference_id=m.reference_id,
        message=m.message,
        is_read=m.is_read,
        created_at=m.created_at,
    )


def hashtag_model_to_entity(m: HashtagModel) -> Hashtag:
    return Hashtag(id=m.id, name=m.name, created_at=m.created_at)
