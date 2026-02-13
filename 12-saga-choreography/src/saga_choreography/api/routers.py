from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from saga_choreography.api.dependencies import get_current_user_id, get_session
from saga_choreography.api.schemas import (
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
from saga_choreography.models.tables import Follow, User
from saga_choreography.sagas import (
    comment_saga,
    create_post_saga,
    create_story_saga,
    delete_post_saga,
    follow_user_saga,
    like_post_saga,
    send_message_saga,
)
from saga_choreography.services import (
    auth_service,
    feed_service,
    follow_service,
    message_service,
    notification_service,
    post_service,
    search_service,
    story_service,
    user_service,
)
from saga_choreography.shared.saga import saga_executor

# --- Auth ---
auth_router = APIRouter(prefix="/api/auth", tags=["auth"])


@auth_router.post("/register", response_model=UserResponse, status_code=201)
async def register(data: UserCreate, db: AsyncSession = Depends(get_session)):
    user = await auth_service.register_user(
        username=data.username,
        email=data.email,
        password=data.password,
        full_name=data.full_name,
        db=db,
    )
    return user


@auth_router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_session)):
    token = await auth_service.login_user(email=data.email, password=data.password, db=db)
    return TokenResponse(access_token=token)


@auth_router.get("/me", response_model=UserResponse)
async def me(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_session),
):
    user = await user_service.get_user_by_id(user_id=user_id, db=db)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


# --- Users ---
user_router = APIRouter(prefix="/api/users", tags=["users"])


@user_router.get("/{user_id}", response_model=UserProfileResponse)
async def get_user(user_id: int, db: AsyncSession = Depends(get_session)):
    profile = await user_service.get_user_profile(user_id=user_id, db=db)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return profile


@user_router.put("/me", response_model=UserResponse)
async def update_me(
    data: UserUpdate,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_session),
):
    return await user_service.update_user(
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
    return await post_service.get_user_posts(user_id=user_id, limit=limit, offset=offset, db=db)


@user_router.get("/{user_id}/followers", response_model=list[UserResponse])
async def list_followers(user_id: int, db: AsyncSession = Depends(get_session)):
    result = await db.execute(
        select(User)
        .join(Follow, Follow.follower_id == User.id)
        .where(Follow.following_id == user_id)
    )
    return result.scalars().all()


@user_router.get("/{user_id}/following", response_model=list[UserResponse])
async def list_following(user_id: int, db: AsyncSession = Depends(get_session)):
    result = await db.execute(
        select(User)
        .join(Follow, Follow.following_id == User.id)
        .where(Follow.follower_id == user_id)
    )
    return result.scalars().all()


# --- Posts (uses sagas for multi-step writes) ---
post_router = APIRouter(prefix="/api/posts", tags=["posts"])


@post_router.post("", response_model=PostResponse, status_code=201)
async def create_post_endpoint(
    data: PostCreate,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_session),
):
    context = {"user_id": user_id, "content": data.content, "image_url": data.image_url}
    steps = create_post_saga.build_steps(db)
    await saga_executor.execute(
        saga_id=str(uuid4()),
        saga_type="create_post",
        steps=steps,
        context=context,
        db=db,
    )
    post = context["post"]
    author = await user_service.get_user_by_id(user_id, db)
    return {
        "id": post.id,
        "author_id": post.author_id,
        "author_username": author.username if author else None,
        "content": post.content,
        "image_url": post.image_url,
        "like_count": post.like_count,
        "comment_count": post.comment_count,
        "created_at": post.created_at,
    }


@post_router.get("/{post_id}", response_model=PostResponse)
async def get_post_endpoint(post_id: int, db: AsyncSession = Depends(get_session)):
    result = await post_service.get_post(post_id=post_id, db=db)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return result


@post_router.delete("/{post_id}", status_code=204)
async def delete_post_endpoint(
    post_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_session),
):
    steps = delete_post_saga.build_steps(post_id=post_id, user_id=user_id, db=db)
    await saga_executor.execute(
        saga_id=str(uuid4()),
        saga_type="delete_post",
        steps=steps,
        context={},
        db=db,
    )


@post_router.post("/{post_id}/likes")
async def toggle_like_endpoint(
    post_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_session),
):
    steps = like_post_saga.build_steps(post_id=post_id, user_id=user_id, db=db)
    context: dict = {}
    await saga_executor.execute(
        saga_id=str(uuid4()),
        saga_type="like_post",
        steps=steps,
        context=context,
        db=db,
    )
    result = context["like_result"]
    return {"liked": result["liked"], "like_count": result["like_count"]}


@post_router.get("/{post_id}/comments", response_model=list[CommentResponse])
async def list_comments(
    post_id: int,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_session),
):
    return await post_service.get_post_comments(post_id=post_id, limit=limit, offset=offset, db=db)


@post_router.post("/{post_id}/comments", response_model=CommentResponse, status_code=201)
async def create_comment_endpoint(
    post_id: int,
    data: CommentCreate,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_session),
):
    steps = comment_saga.build_steps(
        post_id=post_id, author_id=user_id, content=data.content, db=db
    )
    context: dict = {}
    await saga_executor.execute(
        saga_id=str(uuid4()),
        saga_type="create_comment",
        steps=steps,
        context=context,
        db=db,
    )
    comment = context["comment"]
    author = await user_service.get_user_by_id(user_id, db)
    return {
        "id": comment.id,
        "post_id": comment.post_id,
        "author_id": comment.author_id,
        "author_username": author.username if author else None,
        "content": comment.content,
        "created_at": comment.created_at,
    }


@post_router.delete("/comments/{comment_id}", status_code=204)
async def delete_comment_endpoint(
    comment_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_session),
):
    from saga_choreography.services import comment_service
    await comment_service.delete_comment(comment_id=comment_id, user_id=user_id, db=db)


# --- Follow (uses saga) ---
follow_router = APIRouter(prefix="/api/follow", tags=["follow"])


@follow_router.post("/{following_id}")
async def follow_user_endpoint(
    following_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_session),
):
    steps = follow_user_saga.build_steps(
        follower_id=user_id, following_id=following_id, db=db
    )
    await saga_executor.execute(
        saga_id=str(uuid4()),
        saga_type="follow_user",
        steps=steps,
        context={},
        db=db,
    )
    return {"following": True}


@follow_router.delete("/{following_id}")
async def unfollow_user_endpoint(
    following_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_session),
):
    await follow_service.delete_follow(follower_id=user_id, following_id=following_id, db=db)
    return {"following": False}


# --- Feed ---
feed_router = APIRouter(prefix="/api/feed", tags=["feed"])


@feed_router.get("", response_model=list[PostResponse])
async def get_feed_endpoint(
    limit: int = 20,
    offset: int = 0,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_session),
):
    return await feed_service.get_feed(user_id=user_id, limit=limit, offset=offset, db=db)


# --- Stories (uses saga) ---
story_router = APIRouter(prefix="/api/stories", tags=["stories"])


@story_router.post("", response_model=StoryResponse, status_code=201)
async def create_story_endpoint(
    data: StoryCreate,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_session),
):
    steps = create_story_saga.build_steps(
        author_id=user_id, image_url=data.image_url, content=data.content, db=db
    )
    context: dict = {}
    await saga_executor.execute(
        saga_id=str(uuid4()),
        saga_type="create_story",
        steps=steps,
        context=context,
        db=db,
    )
    story = context["story"]
    author = await user_service.get_user_by_id(user_id, db)
    return {
        "id": story.id,
        "author_id": story.author_id,
        "author_username": author.username if author else None,
        "image_url": story.image_url,
        "content": story.content,
        "created_at": story.created_at,
    }


@story_router.get("", response_model=list[StoryResponse])
async def list_my_stories(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_session),
):
    return await story_service.get_my_stories(user_id=user_id, db=db)


@story_router.get("/feed", response_model=list[StoryResponse])
async def get_story_feed_endpoint(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_session),
):
    return await story_service.get_story_feed(user_id=user_id, db=db)


@story_router.delete("/{story_id}", status_code=204)
async def delete_story_endpoint(
    story_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_session),
):
    await story_service.delete_story(story_id=story_id, user_id=user_id, db=db)


# --- Messages (uses saga) ---
message_router = APIRouter(prefix="/api/messages", tags=["messages"])


@message_router.post("", response_model=MessageResponse, status_code=201)
async def send_message_endpoint(
    data: MessageCreate,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_session),
):
    steps = send_message_saga.build_steps(
        sender_id=user_id, receiver_id=data.receiver_id, content=data.content, db=db
    )
    context: dict = {}
    await saga_executor.execute(
        saga_id=str(uuid4()),
        saga_type="send_message",
        steps=steps,
        context=context,
        db=db,
    )
    msg = context["message"]
    return {
        "id": msg.id,
        "sender_id": msg.sender_id,
        "receiver_id": msg.receiver_id,
        "content": msg.content,
        "is_read": msg.is_read,
        "created_at": msg.created_at,
    }


@message_router.get("", response_model=list[ConversationResponse])
async def list_conversations_endpoint(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_session),
):
    return await message_service.get_conversations(user_id=user_id, db=db)


@message_router.get("/{other_user_id}", response_model=list[MessageResponse])
async def get_conversation_endpoint(
    other_user_id: int,
    limit: int = 50,
    offset: int = 0,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_session),
):
    return await message_service.get_conversation(
        user_id=user_id, other_user_id=other_user_id, limit=limit, offset=offset, db=db
    )


@message_router.post("/{sender_id}/read")
async def mark_read_endpoint(
    sender_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_session),
):
    return await message_service.mark_messages_read(user_id=user_id, sender_id=sender_id, db=db)


# --- Notifications ---
notification_router = APIRouter(prefix="/api/notifications", tags=["notifications"])


@notification_router.get("", response_model=list[NotificationResponse])
async def list_notifications_endpoint(
    limit: int = 50,
    offset: int = 0,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_session),
):
    return await notification_service.get_notifications(user_id=user_id, limit=limit, offset=offset, db=db)


@notification_router.post("/{notification_id}/read")
async def mark_notification_read_endpoint(
    notification_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_session),
):
    return await notification_service.mark_notification_read(notification_id=notification_id, user_id=user_id, db=db)


@notification_router.post("/read-all")
async def mark_all_read_endpoint(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_session),
):
    return await notification_service.mark_all_notifications_read(user_id=user_id, db=db)


# --- Search ---
search_router = APIRouter(prefix="/api/search", tags=["search"])


@search_router.get("/users", response_model=list[UserResponse])
async def search_users_endpoint(
    q: str,
    limit: int = 20,
    db: AsyncSession = Depends(get_session),
):
    return await search_service.search_users(query=q, limit=limit, db=db)


@search_router.get("/hashtags", response_model=list[HashtagResponse])
async def search_hashtags_endpoint(
    q: str,
    limit: int = 20,
    db: AsyncSession = Depends(get_session),
):
    return await search_service.search_hashtags(query=q, limit=limit, db=db)


@search_router.get("/posts/hashtag/{tag}", response_model=list[PostResponse])
async def get_posts_by_hashtag_endpoint(
    tag: str,
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_session),
):
    return await search_service.get_posts_by_hashtag(tag=tag, limit=limit, offset=offset, db=db)
