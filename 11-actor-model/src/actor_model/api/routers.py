from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import async_sessionmaker

from actor_model.actors.messages import (
    CreateCommentMessage,
    CreatePostMessage,
    CreateStoryMessage,
    DeleteCommentMessage,
    DeletePostMessage,
    DeleteStoryMessage,
    FollowUserMessage,
    GetCommentsMessage,
    GetConversationMessage,
    GetConversationsMessage,
    GetCurrentUserMessage,
    GetFeedMessage,
    GetFollowersMessage,
    GetFollowingMessage,
    GetPostMessage,
    GetPostsByHashtagMessage,
    GetProfileMessage,
    GetStoriesMessage,
    GetStoryFeedMessage,
    GetUserPostsMessage,
    LoginMessage,
    MarkAllNotificationsReadMessage,
    MarkMessagesReadMessage,
    MarkNotificationReadMessage,
    GetNotificationsMessage,
    RegisterMessage,
    SearchHashtagsMessage,
    SearchUsersMessage,
    SendDirectMessage,
    ToggleLikeMessage,
    UnfollowUserMessage,
    UpdateProfileMessage,
)
from actor_model.actors.registry import ActorRegistry
from actor_model.api.dependencies import get_current_user_id, get_registry
from actor_model.api.schemas import (
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


async def _ask(registry: ActorRegistry, actor_name: str, message):
    await registry.send(actor_name, message)
    try:
        return await message.response()
    except ValueError as e:
        detail = str(e)
        if "not found" in detail.lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
        elif "invalid" in detail.lower() or "credentials" in detail.lower():
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


def _get_db_factory(registry: ActorRegistry) -> async_sessionmaker:
    return registry._db_factory


# --- Auth ---

auth_router = APIRouter(prefix="/api/auth", tags=["auth"])


@auth_router.post("/register", response_model=UserResponse, status_code=201)
async def register(data: UserCreate, registry: ActorRegistry = Depends(get_registry)):
    msg = RegisterMessage(
        username=data.username, email=data.email,
        password=data.password, full_name=data.full_name,
        db_factory=_get_db_factory(registry),
    )
    result = await _ask(registry, "user", msg)
    return result


@auth_router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, registry: ActorRegistry = Depends(get_registry)):
    msg = LoginMessage(email=data.email, password=data.password, db_factory=_get_db_factory(registry))
    return await _ask(registry, "user", msg)


@auth_router.get("/me", response_model=UserResponse)
async def me(
    user_id: int = Depends(get_current_user_id),
    registry: ActorRegistry = Depends(get_registry),
):
    msg = GetCurrentUserMessage(user_id=user_id, db_factory=_get_db_factory(registry))
    return await _ask(registry, "user", msg)


# --- Users ---

user_router = APIRouter(prefix="/api/users", tags=["users"])


@user_router.get("/{user_id}", response_model=UserProfileResponse)
async def get_user(user_id: int, registry: ActorRegistry = Depends(get_registry)):
    msg = GetProfileMessage(user_id=user_id, db_factory=_get_db_factory(registry))
    return await _ask(registry, "user", msg)


@user_router.put("/me", response_model=UserResponse)
async def update_me(
    data: UserUpdate,
    user_id: int = Depends(get_current_user_id),
    registry: ActorRegistry = Depends(get_registry),
):
    msg = UpdateProfileMessage(
        user_id=user_id,
        update_data=data.model_dump(exclude_unset=True),
        db_factory=_get_db_factory(registry),
    )
    return await _ask(registry, "user", msg)


@user_router.get("/{user_id}/posts", response_model=list[PostResponse])
async def get_user_posts(
    user_id: int, limit: int = 20, offset: int = 0,
    registry: ActorRegistry = Depends(get_registry),
):
    msg = GetUserPostsMessage(
        user_id=user_id, limit=limit, offset=offset,
        db_factory=_get_db_factory(registry),
    )
    return await _ask(registry, "post", msg)


@user_router.get("/{user_id}/followers", response_model=list[UserResponse])
async def get_followers(user_id: int, registry: ActorRegistry = Depends(get_registry)):
    msg = GetFollowersMessage(user_id=user_id, db_factory=_get_db_factory(registry))
    return await _ask(registry, "user", msg)


@user_router.get("/{user_id}/following", response_model=list[UserResponse])
async def get_following(user_id: int, registry: ActorRegistry = Depends(get_registry)):
    msg = GetFollowingMessage(user_id=user_id, db_factory=_get_db_factory(registry))
    return await _ask(registry, "user", msg)


# --- Posts ---

post_router = APIRouter(prefix="/api/posts", tags=["posts"])


@post_router.post("", response_model=PostResponse, status_code=201)
async def create_post(
    data: PostCreate,
    user_id: int = Depends(get_current_user_id),
    registry: ActorRegistry = Depends(get_registry),
):
    msg = CreatePostMessage(
        author_id=user_id, content=data.content, image_url=data.image_url,
        db_factory=_get_db_factory(registry),
    )
    return await _ask(registry, "post", msg)


@post_router.get("/{post_id}", response_model=PostResponse)
async def get_post(post_id: int, registry: ActorRegistry = Depends(get_registry)):
    msg = GetPostMessage(post_id=post_id, db_factory=_get_db_factory(registry))
    return await _ask(registry, "post", msg)


@post_router.delete("/{post_id}", status_code=204)
async def delete_post(
    post_id: int,
    user_id: int = Depends(get_current_user_id),
    registry: ActorRegistry = Depends(get_registry),
):
    msg = DeletePostMessage(post_id=post_id, user_id=user_id, db_factory=_get_db_factory(registry))
    await _ask(registry, "post", msg)


@post_router.post("/{post_id}/likes")
async def toggle_like(
    post_id: int,
    user_id: int = Depends(get_current_user_id),
    registry: ActorRegistry = Depends(get_registry),
):
    msg = ToggleLikeMessage(post_id=post_id, user_id=user_id, db_factory=_get_db_factory(registry))
    return await _ask(registry, "like", msg)


@post_router.get("/{post_id}/comments", response_model=list[CommentResponse])
async def get_comments(
    post_id: int, limit: int = 50, offset: int = 0,
    registry: ActorRegistry = Depends(get_registry),
):
    msg = GetCommentsMessage(
        post_id=post_id, limit=limit, offset=offset,
        db_factory=_get_db_factory(registry),
    )
    return await _ask(registry, "comment", msg)


@post_router.post("/{post_id}/comments", response_model=CommentResponse, status_code=201)
async def create_comment(
    post_id: int,
    data: CommentCreate,
    user_id: int = Depends(get_current_user_id),
    registry: ActorRegistry = Depends(get_registry),
):
    msg = CreateCommentMessage(
        post_id=post_id, author_id=user_id, content=data.content,
        db_factory=_get_db_factory(registry),
    )
    return await _ask(registry, "comment", msg)


@post_router.delete("/comments/{comment_id}", status_code=204)
async def delete_comment(
    comment_id: int,
    user_id: int = Depends(get_current_user_id),
    registry: ActorRegistry = Depends(get_registry),
):
    msg = DeleteCommentMessage(comment_id=comment_id, user_id=user_id, db_factory=_get_db_factory(registry))
    await _ask(registry, "comment", msg)


# --- Follow ---

follow_router = APIRouter(prefix="/api/follow", tags=["follow"])


@follow_router.post("/{following_id}")
async def follow_user(
    following_id: int,
    user_id: int = Depends(get_current_user_id),
    registry: ActorRegistry = Depends(get_registry),
):
    msg = FollowUserMessage(
        follower_id=user_id, following_id=following_id,
        db_factory=_get_db_factory(registry),
    )
    return await _ask(registry, "follow", msg)


@follow_router.delete("/{following_id}")
async def unfollow_user(
    following_id: int,
    user_id: int = Depends(get_current_user_id),
    registry: ActorRegistry = Depends(get_registry),
):
    msg = UnfollowUserMessage(
        follower_id=user_id, following_id=following_id,
        db_factory=_get_db_factory(registry),
    )
    return await _ask(registry, "follow", msg)


# --- Feed ---

feed_router = APIRouter(prefix="/api/feed", tags=["feed"])


@feed_router.get("", response_model=list[PostResponse])
async def get_feed(
    limit: int = 20, offset: int = 0,
    user_id: int = Depends(get_current_user_id),
    registry: ActorRegistry = Depends(get_registry),
):
    msg = GetFeedMessage(
        user_id=user_id, limit=limit, offset=offset,
        db_factory=_get_db_factory(registry),
    )
    return await _ask(registry, "feed", msg)


# --- Stories ---

story_router = APIRouter(prefix="/api/stories", tags=["stories"])


@story_router.post("", response_model=StoryResponse, status_code=201)
async def create_story(
    data: StoryCreate,
    user_id: int = Depends(get_current_user_id),
    registry: ActorRegistry = Depends(get_registry),
):
    msg = CreateStoryMessage(
        author_id=user_id, image_url=data.image_url, content=data.content,
        db_factory=_get_db_factory(registry),
    )
    return await _ask(registry, "story", msg)


@story_router.get("", response_model=list[StoryResponse])
async def get_my_stories(
    user_id: int = Depends(get_current_user_id),
    registry: ActorRegistry = Depends(get_registry),
):
    msg = GetStoriesMessage(user_id=user_id, db_factory=_get_db_factory(registry))
    return await _ask(registry, "story", msg)


@story_router.get("/feed", response_model=list[StoryResponse])
async def get_story_feed(
    user_id: int = Depends(get_current_user_id),
    registry: ActorRegistry = Depends(get_registry),
):
    msg = GetStoryFeedMessage(user_id=user_id, db_factory=_get_db_factory(registry))
    return await _ask(registry, "story", msg)


@story_router.delete("/{story_id}", status_code=204)
async def delete_story(
    story_id: int,
    user_id: int = Depends(get_current_user_id),
    registry: ActorRegistry = Depends(get_registry),
):
    msg = DeleteStoryMessage(story_id=story_id, user_id=user_id, db_factory=_get_db_factory(registry))
    await _ask(registry, "story", msg)


# --- Messages ---

message_router = APIRouter(prefix="/api/messages", tags=["messages"])


@message_router.post("", response_model=MessageResponse, status_code=201)
async def send_message(
    data: MessageCreate,
    user_id: int = Depends(get_current_user_id),
    registry: ActorRegistry = Depends(get_registry),
):
    msg = SendDirectMessage(
        sender_id=user_id, receiver_id=data.receiver_id, content=data.content,
        db_factory=_get_db_factory(registry),
    )
    return await _ask(registry, "message", msg)


@message_router.get("", response_model=list[ConversationResponse])
async def list_conversations(
    user_id: int = Depends(get_current_user_id),
    registry: ActorRegistry = Depends(get_registry),
):
    msg = GetConversationsMessage(user_id=user_id, db_factory=_get_db_factory(registry))
    return await _ask(registry, "message", msg)


@message_router.get("/{other_user_id}", response_model=list[MessageResponse])
async def get_conversation(
    other_user_id: int,
    limit: int = 50, offset: int = 0,
    user_id: int = Depends(get_current_user_id),
    registry: ActorRegistry = Depends(get_registry),
):
    msg = GetConversationMessage(
        user_id=user_id, other_user_id=other_user_id,
        limit=limit, offset=offset,
        db_factory=_get_db_factory(registry),
    )
    return await _ask(registry, "message", msg)


@message_router.post("/{sender_id}/read")
async def mark_read(
    sender_id: int,
    user_id: int = Depends(get_current_user_id),
    registry: ActorRegistry = Depends(get_registry),
):
    msg = MarkMessagesReadMessage(
        user_id=user_id, sender_id=sender_id,
        db_factory=_get_db_factory(registry),
    )
    return await _ask(registry, "message", msg)


# --- Notifications ---

notification_router = APIRouter(prefix="/api/notifications", tags=["notifications"])


@notification_router.get("", response_model=list[NotificationResponse])
async def list_notifications(
    limit: int = 50, offset: int = 0,
    user_id: int = Depends(get_current_user_id),
    registry: ActorRegistry = Depends(get_registry),
):
    msg = GetNotificationsMessage(
        user_id=user_id, limit=limit, offset=offset,
        db_factory=_get_db_factory(registry),
    )
    return await _ask(registry, "notification", msg)


@notification_router.post("/{notification_id}/read")
async def mark_notification_read(
    notification_id: int,
    user_id: int = Depends(get_current_user_id),
    registry: ActorRegistry = Depends(get_registry),
):
    msg = MarkNotificationReadMessage(
        notification_id=notification_id, user_id=user_id,
        db_factory=_get_db_factory(registry),
    )
    return await _ask(registry, "notification", msg)


@notification_router.post("/read-all")
async def mark_all_read(
    user_id: int = Depends(get_current_user_id),
    registry: ActorRegistry = Depends(get_registry),
):
    msg = MarkAllNotificationsReadMessage(
        user_id=user_id, db_factory=_get_db_factory(registry),
    )
    return await _ask(registry, "notification", msg)


# --- Search ---

search_router = APIRouter(prefix="/api/search", tags=["search"])


@search_router.get("/users", response_model=list[UserResponse])
async def search_users(
    q: str, limit: int = 20,
    registry: ActorRegistry = Depends(get_registry),
):
    msg = SearchUsersMessage(query=q, limit=limit, db_factory=_get_db_factory(registry))
    return await _ask(registry, "search", msg)


@search_router.get("/hashtags", response_model=list[HashtagResponse])
async def search_hashtags(
    q: str, limit: int = 20,
    registry: ActorRegistry = Depends(get_registry),
):
    msg = SearchHashtagsMessage(query=q, limit=limit, db_factory=_get_db_factory(registry))
    return await _ask(registry, "search", msg)


@search_router.get("/posts/hashtag/{tag}", response_model=list[PostResponse])
async def get_posts_by_hashtag(
    tag: str, limit: int = 20, offset: int = 0,
    registry: ActorRegistry = Depends(get_registry),
):
    msg = GetPostsByHashtagMessage(
        tag=tag, limit=limit, offset=offset,
        db_factory=_get_db_factory(registry),
    )
    return await _ask(registry, "search", msg)
