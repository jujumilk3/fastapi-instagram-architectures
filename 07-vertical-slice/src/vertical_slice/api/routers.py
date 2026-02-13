from __future__ import annotations

from dataclasses import asdict

from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession

from vertical_slice.api.schemas import (
    CommentCreateBody,
    CommentOut,
    ConversationOut,
    FollowOut,
    HashtagOut,
    LikeOut,
    LoginBody,
    MessageCreateBody,
    MessageOut,
    NotificationOut,
    PostCreateBody,
    PostOut,
    StatusOut,
    StoryCreateBody,
    StoryOut,
    TokenOut,
    UserCreateBody,
    UserOut,
    UserProfileOut,
    UserUpdateBody,
)
from vertical_slice.shared.database import get_db
from vertical_slice.shared.mediator import mediator
from vertical_slice.shared.security import get_current_user_id

from vertical_slice.features.auth.register import RegisterRequest
from vertical_slice.features.auth.login import LoginRequest
from vertical_slice.features.auth.get_me import GetMeRequest
from vertical_slice.features.user.get_profile import GetProfileRequest
from vertical_slice.features.user.update_profile import UpdateProfileRequest
from vertical_slice.features.user.get_user_posts import GetUserPostsRequest
from vertical_slice.features.user.get_followers import GetFollowersRequest
from vertical_slice.features.user.get_following import GetFollowingRequest
from vertical_slice.features.post.create_post import CreatePostRequest
from vertical_slice.features.post.get_post import GetPostRequest
from vertical_slice.features.post.delete_post import DeletePostRequest
from vertical_slice.features.comment.create_comment import CreateCommentRequest
from vertical_slice.features.comment.get_comments import GetCommentsRequest
from vertical_slice.features.comment.delete_comment import DeleteCommentRequest
from vertical_slice.features.like.toggle_like import ToggleLikeRequest
from vertical_slice.features.follow.follow_user import FollowUserRequest
from vertical_slice.features.follow.unfollow_user import UnfollowUserRequest
from vertical_slice.features.feed.get_feed import GetFeedRequest
from vertical_slice.features.story.create_story import CreateStoryRequest
from vertical_slice.features.story.get_my_stories import GetMyStoriesRequest
from vertical_slice.features.story.get_story_feed import GetStoryFeedRequest
from vertical_slice.features.story.delete_story import DeleteStoryRequest
from vertical_slice.features.message.send_message import SendMessageRequest
from vertical_slice.features.message.get_conversations import GetConversationsRequest
from vertical_slice.features.message.get_conversation import GetConversationRequest
from vertical_slice.features.message.mark_messages_read import MarkMessagesReadRequest
from vertical_slice.features.notification.get_notifications import GetNotificationsRequest
from vertical_slice.features.notification.mark_notification_read import MarkNotificationReadRequest
from vertical_slice.features.notification.mark_all_read import MarkAllReadRequest
from vertical_slice.features.search.search_users import SearchUsersRequest
from vertical_slice.features.search.search_hashtags import SearchHashtagsRequest
from vertical_slice.features.search.get_posts_by_hashtag import GetPostsByHashtagRequest

# ── Auth ──

auth_router = APIRouter(prefix="/api/auth", tags=["auth"])


@auth_router.post("/register", response_model=UserOut, status_code=201)
async def register(body: UserCreateBody, db: AsyncSession = Depends(get_db)):
    result = await mediator.send(RegisterRequest(
        username=body.username, email=body.email,
        password=body.password, full_name=body.full_name, db=db,
    ))
    return asdict(result)


@auth_router.post("/login", response_model=TokenOut)
async def login(body: LoginBody, db: AsyncSession = Depends(get_db)):
    result = await mediator.send(LoginRequest(email=body.email, password=body.password, db=db))
    return asdict(result)


@auth_router.get("/me", response_model=UserOut)
async def me(user_id: int = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    result = await mediator.send(GetMeRequest(user_id=user_id, db=db))
    return asdict(result)


# ── User ──

user_router = APIRouter(prefix="/api/users", tags=["users"])


@user_router.get("/{user_id}", response_model=UserProfileOut)
async def get_profile(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await mediator.send(GetProfileRequest(user_id=user_id, db=db))
    return asdict(result)


@user_router.put("/me", response_model=UserOut)
async def update_me(body: UserUpdateBody, user_id: int = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    result = await mediator.send(UpdateProfileRequest(
        user_id=user_id, data=body.model_dump(exclude_unset=True), db=db,
    ))
    return asdict(result)


@user_router.get("/{user_id}/posts", response_model=list[PostOut])
async def get_user_posts(user_id: int, limit: int = 20, offset: int = 0, db: AsyncSession = Depends(get_db)):
    result = await mediator.send(GetUserPostsRequest(user_id=user_id, limit=limit, offset=offset, db=db))
    return [asdict(p) for p in result]


@user_router.get("/{user_id}/followers", response_model=list[UserOut])
async def get_followers(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await mediator.send(GetFollowersRequest(user_id=user_id, db=db))
    return [asdict(u) for u in result]


@user_router.get("/{user_id}/following", response_model=list[UserOut])
async def get_following(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await mediator.send(GetFollowingRequest(user_id=user_id, db=db))
    return [asdict(u) for u in result]


# ── Post ──

post_router = APIRouter(prefix="/api/posts", tags=["posts"])


@post_router.post("", response_model=PostOut, status_code=201)
async def create_post(body: PostCreateBody, user_id: int = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    result = await mediator.send(CreatePostRequest(
        author_id=user_id, content=body.content, image_url=body.image_url, db=db,
    ))
    return asdict(result)


@post_router.get("/{post_id}", response_model=PostOut)
async def get_post(post_id: int, db: AsyncSession = Depends(get_db)):
    result = await mediator.send(GetPostRequest(post_id=post_id, db=db))
    return asdict(result)


@post_router.delete("/{post_id}", status_code=204)
async def delete_post(post_id: int, user_id: int = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    await mediator.send(DeletePostRequest(post_id=post_id, user_id=user_id, db=db))
    return Response(status_code=204)


# ── Comment ──

@post_router.post("/{post_id}/comments", response_model=CommentOut, status_code=201)
async def create_comment(post_id: int, body: CommentCreateBody, user_id: int = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    result = await mediator.send(CreateCommentRequest(
        post_id=post_id, author_id=user_id, content=body.content, db=db,
    ))
    return asdict(result)


@post_router.get("/{post_id}/comments", response_model=list[CommentOut])
async def get_comments(post_id: int, limit: int = 50, offset: int = 0, db: AsyncSession = Depends(get_db)):
    result = await mediator.send(GetCommentsRequest(post_id=post_id, limit=limit, offset=offset, db=db))
    return [asdict(c) for c in result]


@post_router.delete("/comments/{comment_id}", status_code=204)
async def delete_comment(comment_id: int, user_id: int = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    await mediator.send(DeleteCommentRequest(comment_id=comment_id, user_id=user_id, db=db))
    return Response(status_code=204)


# ── Like ──

@post_router.post("/{post_id}/likes", response_model=LikeOut)
async def toggle_like(post_id: int, user_id: int = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    result = await mediator.send(ToggleLikeRequest(post_id=post_id, user_id=user_id, db=db))
    return asdict(result)


# ── Follow ──

follow_router = APIRouter(prefix="/api/follow", tags=["follow"])


@follow_router.post("/{following_id}", response_model=FollowOut)
async def follow_user(following_id: int, user_id: int = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    result = await mediator.send(FollowUserRequest(follower_id=user_id, following_id=following_id, db=db))
    return asdict(result)


@follow_router.delete("/{following_id}", response_model=FollowOut)
async def unfollow_user(following_id: int, user_id: int = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    result = await mediator.send(UnfollowUserRequest(follower_id=user_id, following_id=following_id, db=db))
    return asdict(result)


# ── Feed ──

feed_router = APIRouter(prefix="/api/feed", tags=["feed"])


@feed_router.get("", response_model=list[PostOut])
async def get_feed(limit: int = 20, offset: int = 0, user_id: int = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    result = await mediator.send(GetFeedRequest(user_id=user_id, limit=limit, offset=offset, db=db))
    return [asdict(p) for p in result]


# ── Story ──

story_router = APIRouter(prefix="/api/stories", tags=["stories"])


@story_router.post("", response_model=StoryOut, status_code=201)
async def create_story(body: StoryCreateBody, user_id: int = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    result = await mediator.send(CreateStoryRequest(
        author_id=user_id, image_url=body.image_url, content=body.content, db=db,
    ))
    return asdict(result)


@story_router.get("", response_model=list[StoryOut])
async def get_my_stories(user_id: int = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    result = await mediator.send(GetMyStoriesRequest(user_id=user_id, db=db))
    return [asdict(s) for s in result]


@story_router.get("/feed", response_model=list[StoryOut])
async def get_story_feed(user_id: int = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    result = await mediator.send(GetStoryFeedRequest(user_id=user_id, db=db))
    return [asdict(s) for s in result]


@story_router.delete("/{story_id}", status_code=204)
async def delete_story(story_id: int, user_id: int = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    await mediator.send(DeleteStoryRequest(story_id=story_id, user_id=user_id, db=db))
    return Response(status_code=204)


# ── Message ──

message_router = APIRouter(prefix="/api/messages", tags=["messages"])


@message_router.post("", response_model=MessageOut, status_code=201)
async def send_message(body: MessageCreateBody, user_id: int = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    result = await mediator.send(SendMessageRequest(
        sender_id=user_id, receiver_id=body.receiver_id, content=body.content, db=db,
    ))
    return asdict(result)


@message_router.get("", response_model=list[ConversationOut])
async def get_conversations(user_id: int = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    result = await mediator.send(GetConversationsRequest(user_id=user_id, db=db))
    return [asdict(c) for c in result]


@message_router.get("/{other_user_id}", response_model=list[MessageOut])
async def get_conversation(other_user_id: int, limit: int = 50, offset: int = 0, user_id: int = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    result = await mediator.send(GetConversationRequest(
        user_id=user_id, other_user_id=other_user_id, limit=limit, offset=offset, db=db,
    ))
    return [asdict(m) for m in result]


@message_router.post("/{sender_id}/read", response_model=StatusOut)
async def mark_messages_read(sender_id: int, user_id: int = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    result = await mediator.send(MarkMessagesReadRequest(user_id=user_id, sender_id=sender_id, db=db))
    return result


# ── Notification ──

notification_router = APIRouter(prefix="/api/notifications", tags=["notifications"])


@notification_router.get("", response_model=list[NotificationOut])
async def get_notifications(limit: int = 50, offset: int = 0, user_id: int = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    result = await mediator.send(GetNotificationsRequest(user_id=user_id, limit=limit, offset=offset, db=db))
    return [asdict(n) for n in result]


@notification_router.post("/{notification_id}/read", response_model=StatusOut)
async def mark_notification_read(notification_id: int, user_id: int = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    result = await mediator.send(MarkNotificationReadRequest(notification_id=notification_id, user_id=user_id, db=db))
    return result


@notification_router.post("/read-all", response_model=StatusOut)
async def mark_all_read(user_id: int = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    result = await mediator.send(MarkAllReadRequest(user_id=user_id, db=db))
    return result


# ── Search ──

search_router = APIRouter(prefix="/api/search", tags=["search"])


@search_router.get("/users", response_model=list[UserOut])
async def search_users(q: str = "", limit: int = 20, db: AsyncSession = Depends(get_db)):
    result = await mediator.send(SearchUsersRequest(query=q, limit=limit, db=db))
    return [asdict(u) for u in result]


@search_router.get("/hashtags", response_model=list[HashtagOut])
async def search_hashtags(q: str = "", limit: int = 20, db: AsyncSession = Depends(get_db)):
    result = await mediator.send(SearchHashtagsRequest(query=q, limit=limit, db=db))
    return [asdict(h) for h in result]


@search_router.get("/posts/hashtag/{tag}", response_model=list[PostOut])
async def get_posts_by_hashtag(tag: str, limit: int = 20, offset: int = 0, db: AsyncSession = Depends(get_db)):
    result = await mediator.send(GetPostsByHashtagRequest(tag=tag, limit=limit, offset=offset, db=db))
    return [asdict(p) for p in result]
