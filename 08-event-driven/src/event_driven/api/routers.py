from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from event_driven.api.dependencies import get_current_user_id, get_session
from event_driven.api.schemas import (
    CommentCreate,
    CommentResponse,
    ConversationResponse,
    HashtagResponse,
    LoginRequest,
    MessageCreate,
    MessageResponse,
    NotificationResponse,
    PostCreate,
    PostResponse,
    StoryCreate,
    StoryResponse,
    TokenResponse,
    UserCreate,
    UserProfileResponse,
    UserResponse,
    UserUpdate,
)
from event_driven.producers.auth_producer import login_user, register_user, update_user
from event_driven.producers.comment_producer import create_comment, delete_comment
from event_driven.producers.follow_producer import follow_user, unfollow_user
from event_driven.producers.like_producer import toggle_like
from event_driven.producers.message_producer import (
    mark_all_notifications_read,
    mark_messages_read,
    mark_notification_read,
    send_message,
)
from event_driven.producers.post_producer import create_post, delete_post
from event_driven.producers.story_producer import create_story, delete_story
from event_driven.queries.feed_queries import get_feed
from event_driven.queries.message_queries import get_conversation, get_conversations
from event_driven.queries.notification_queries import get_notifications
from event_driven.queries.post_queries import get_post, get_post_comments, get_user_posts
from event_driven.queries.search_queries import get_posts_by_hashtag, search_hashtags, search_users
from event_driven.queries.story_queries import get_my_stories, get_story_feed
from event_driven.queries.user_queries import get_user_by_id, get_user_profile

# --- Auth ---
auth_router = APIRouter(prefix="/api/auth", tags=["auth"])


@auth_router.post("/register", response_model=UserResponse, status_code=201)
async def register(data: UserCreate, db: AsyncSession = Depends(get_session)):
    user = await register_user(
        username=data.username,
        email=data.email,
        password=data.password,
        full_name=data.full_name,
        db=db,
    )
    return user


@auth_router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_session)):
    token = await login_user(email=data.email, password=data.password, db=db)
    return TokenResponse(access_token=token)


@auth_router.get("/me", response_model=UserResponse)
async def me(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_session),
):
    user = await get_user_by_id(user_id=user_id, db=db)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


# --- Users ---
user_router = APIRouter(prefix="/api/users", tags=["users"])


@user_router.get("/{user_id}", response_model=UserProfileResponse)
async def get_user(user_id: int, db: AsyncSession = Depends(get_session)):
    profile = await get_user_profile(user_id=user_id, db=db)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return profile


@user_router.put("/me", response_model=UserResponse)
async def update_me(
    data: UserUpdate,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_session),
):
    return await update_user(
        user_id=user_id,
        full_name=data.full_name,
        bio=data.bio,
        profile_image_url=data.profile_image_url,
        db=db,
    )


@user_router.get("/{user_id}/posts", response_model=list[PostResponse])
async def list_user_posts(
    user_id: int,
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_session),
):
    return await get_user_posts(user_id=user_id, limit=limit, offset=offset, db=db)


@user_router.get("/{user_id}/followers", response_model=list[UserResponse])
async def list_followers(user_id: int, db: AsyncSession = Depends(get_session)):
    from event_driven.models.tables import Follow, User
    from sqlalchemy import select

    result = await db.execute(
        select(User)
        .join(Follow, Follow.follower_id == User.id)
        .where(Follow.following_id == user_id)
    )
    users = result.scalars().all()
    return users


@user_router.get("/{user_id}/following", response_model=list[UserResponse])
async def list_following(user_id: int, db: AsyncSession = Depends(get_session)):
    from event_driven.models.tables import Follow, User
    from sqlalchemy import select

    result = await db.execute(
        select(User)
        .join(Follow, Follow.following_id == User.id)
        .where(Follow.follower_id == user_id)
    )
    users = result.scalars().all()
    return users


# --- Posts ---
post_router = APIRouter(prefix="/api/posts", tags=["posts"])


@post_router.post("", response_model=PostResponse, status_code=201)
async def create_post_endpoint(
    data: PostCreate,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_session),
):
    return await create_post(author_id=user_id, content=data.content, image_url=data.image_url, db=db)


@post_router.get("/{post_id}", response_model=PostResponse)
async def get_post_endpoint(post_id: int, db: AsyncSession = Depends(get_session)):
    result = await get_post(post_id=post_id, db=db)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return result


@post_router.delete("/{post_id}", status_code=204)
async def delete_post_endpoint(
    post_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_session),
):
    await delete_post(post_id=post_id, user_id=user_id, db=db)


@post_router.post("/{post_id}/likes")
async def toggle_like_endpoint(
    post_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_session),
):
    return await toggle_like(post_id=post_id, user_id=user_id, db=db)


@post_router.get("/{post_id}/comments", response_model=list[CommentResponse])
async def list_comments(
    post_id: int,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_session),
):
    return await get_post_comments(post_id=post_id, limit=limit, offset=offset, db=db)


@post_router.post("/{post_id}/comments", response_model=CommentResponse, status_code=201)
async def create_comment_endpoint(
    post_id: int,
    data: CommentCreate,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_session),
):
    return await create_comment(post_id=post_id, author_id=user_id, content=data.content, db=db)


@post_router.delete("/comments/{comment_id}", status_code=204)
async def delete_comment_endpoint(
    comment_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_session),
):
    await delete_comment(comment_id=comment_id, user_id=user_id, db=db)


# --- Follow ---
follow_router = APIRouter(prefix="/api/follow", tags=["follow"])


@follow_router.post("/{following_id}")
async def follow_user_endpoint(
    following_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_session),
):
    return await follow_user(follower_id=user_id, following_id=following_id, db=db)


@follow_router.delete("/{following_id}")
async def unfollow_user_endpoint(
    following_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_session),
):
    return await unfollow_user(follower_id=user_id, following_id=following_id, db=db)


# --- Feed ---
feed_router = APIRouter(prefix="/api/feed", tags=["feed"])


@feed_router.get("", response_model=list[PostResponse])
async def get_feed_endpoint(
    limit: int = 20,
    offset: int = 0,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_session),
):
    return await get_feed(user_id=user_id, limit=limit, offset=offset, db=db)


# --- Stories ---
story_router = APIRouter(prefix="/api/stories", tags=["stories"])


@story_router.post("", response_model=StoryResponse, status_code=201)
async def create_story_endpoint(
    data: StoryCreate,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_session),
):
    return await create_story(author_id=user_id, image_url=data.image_url, content=data.content, db=db)


@story_router.get("", response_model=list[StoryResponse])
async def list_my_stories(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_session),
):
    return await get_my_stories(user_id=user_id, db=db)


@story_router.get("/feed", response_model=list[StoryResponse])
async def get_story_feed_endpoint(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_session),
):
    return await get_story_feed(user_id=user_id, db=db)


@story_router.delete("/{story_id}", status_code=204)
async def delete_story_endpoint(
    story_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_session),
):
    await delete_story(story_id=story_id, user_id=user_id, db=db)


# --- Messages ---
message_router = APIRouter(prefix="/api/messages", tags=["messages"])


@message_router.post("", response_model=MessageResponse, status_code=201)
async def send_message_endpoint(
    data: MessageCreate,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_session),
):
    return await send_message(sender_id=user_id, receiver_id=data.receiver_id, content=data.content, db=db)


@message_router.get("", response_model=list[ConversationResponse])
async def list_conversations_endpoint(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_session),
):
    return await get_conversations(user_id=user_id, db=db)


@message_router.get("/{other_user_id}", response_model=list[MessageResponse])
async def get_conversation_endpoint(
    other_user_id: int,
    limit: int = 50,
    offset: int = 0,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_session),
):
    return await get_conversation(
        user_id=user_id, other_user_id=other_user_id, limit=limit, offset=offset, db=db
    )


@message_router.post("/{sender_id}/read")
async def mark_read_endpoint(
    sender_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_session),
):
    return await mark_messages_read(user_id=user_id, sender_id=sender_id, db=db)


# --- Notifications ---
notification_router = APIRouter(prefix="/api/notifications", tags=["notifications"])


@notification_router.get("", response_model=list[NotificationResponse])
async def list_notifications_endpoint(
    limit: int = 50,
    offset: int = 0,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_session),
):
    return await get_notifications(user_id=user_id, limit=limit, offset=offset, db=db)


@notification_router.post("/{notification_id}/read")
async def mark_notification_read_endpoint(
    notification_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_session),
):
    return await mark_notification_read(notification_id=notification_id, user_id=user_id, db=db)


@notification_router.post("/read-all")
async def mark_all_read_endpoint(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_session),
):
    return await mark_all_notifications_read(user_id=user_id, db=db)


# --- Search ---
search_router = APIRouter(prefix="/api/search", tags=["search"])


@search_router.get("/users", response_model=list[UserResponse])
async def search_users_endpoint(
    q: str,
    limit: int = 20,
    db: AsyncSession = Depends(get_session),
):
    return await search_users(query=q, limit=limit, db=db)


@search_router.get("/hashtags", response_model=list[HashtagResponse])
async def search_hashtags_endpoint(
    q: str,
    limit: int = 20,
    db: AsyncSession = Depends(get_session),
):
    return await search_hashtags(query=q, limit=limit, db=db)


@search_router.get("/posts/hashtag/{tag}", response_model=list[PostResponse])
async def get_posts_by_hashtag_endpoint(
    tag: str,
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_session),
):
    return await get_posts_by_hashtag(tag=tag, limit=limit, offset=offset, db=db)
