from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from cqrs_es.api.dependencies import get_current_user_id, get_session
from cqrs_es.api.schemas import (
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
    GetUserFollowers,
    GetUserFollowing,
    GetUserPosts,
    GetUserProfile,
    SearchHashtags,
    SearchUsers,
)
from cqrs_es.shared.command_bus import dispatch_command
from cqrs_es.shared.query_bus import dispatch_query
from cqrs_es.write.commands.commands import (
    CreateComment,
    CreatePost,
    CreateStory,
    DeleteComment,
    DeletePost,
    DeleteStory,
    FollowUser,
    LoginUser,
    MarkAllNotificationsRead,
    MarkMessagesRead,
    MarkNotificationRead,
    RegisterUser,
    SendMessage,
    ToggleLike,
    UnfollowUser,
    UpdateUser,
)

# --- Auth ---
auth_router = APIRouter(prefix="/api/auth", tags=["auth"])


@auth_router.post("/register", response_model=UserResponse, status_code=201)
async def register(data: UserCreate, db: AsyncSession = Depends(get_session)):
    result = await dispatch_command(
        RegisterUser(
            username=data.username, email=data.email,
            password=data.password, full_name=data.full_name, db=db,
        )
    )
    return result


@auth_router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_session)):
    token = await dispatch_command(
        LoginUser(email=data.email, password=data.password, db=db)
    )
    return TokenResponse(access_token=token)


@auth_router.get("/me", response_model=UserResponse)
async def me(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_session),
):
    user = await dispatch_query(GetUserById(user_id=user_id, db=db))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return {
        "id": user.id, "username": user.username, "email": user.email,
        "full_name": user.full_name, "bio": user.bio,
        "profile_image_url": user.profile_image_url,
        "is_active": user.is_active, "created_at": user.created_at,
    }


# --- Users ---
user_router = APIRouter(prefix="/api/users", tags=["users"])


@user_router.get("/{user_id}", response_model=UserProfileResponse)
async def get_user(user_id: int, db: AsyncSession = Depends(get_session)):
    profile = await dispatch_query(GetUserProfile(user_id=user_id, db=db))
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return profile


@user_router.put("/me", response_model=UserResponse)
async def update_me(
    data: UserUpdate,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_session),
):
    return await dispatch_command(
        UpdateUser(
            user_id=user_id, full_name=data.full_name,
            bio=data.bio, profile_image_url=data.profile_image_url, db=db,
        )
    )


@user_router.get("/{user_id}/posts", response_model=list[PostResponse])
async def get_user_posts(
    user_id: int, limit: int = 20, offset: int = 0,
    db: AsyncSession = Depends(get_session),
):
    return await dispatch_query(
        GetUserPosts(user_id=user_id, limit=limit, offset=offset, db=db)
    )


@user_router.get("/{user_id}/followers", response_model=list[UserResponse])
async def get_followers(user_id: int, db: AsyncSession = Depends(get_session)):
    return await dispatch_query(GetUserFollowers(user_id=user_id, db=db))


@user_router.get("/{user_id}/following", response_model=list[UserResponse])
async def get_following(user_id: int, db: AsyncSession = Depends(get_session)):
    return await dispatch_query(GetUserFollowing(user_id=user_id, db=db))


# --- Posts ---
post_router = APIRouter(prefix="/api/posts", tags=["posts"])


@post_router.post("", response_model=PostResponse, status_code=201)
async def create_post(
    data: PostCreate,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_session),
):
    return await dispatch_command(
        CreatePost(author_id=user_id, content=data.content, image_url=data.image_url, db=db)
    )


@post_router.get("/{post_id}", response_model=PostResponse)
async def get_post(post_id: int, db: AsyncSession = Depends(get_session)):
    result = await dispatch_query(GetPost(post_id=post_id, db=db))
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return result


@post_router.delete("/{post_id}", status_code=204)
async def delete_post(
    post_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_session),
):
    await dispatch_command(DeletePost(post_id=post_id, user_id=user_id, db=db))


@post_router.post("/{post_id}/likes")
async def toggle_like(
    post_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_session),
):
    return await dispatch_command(ToggleLike(post_id=post_id, user_id=user_id, db=db))


@post_router.get("/{post_id}/comments", response_model=list[CommentResponse])
async def get_comments(
    post_id: int, limit: int = 50, offset: int = 0,
    db: AsyncSession = Depends(get_session),
):
    return await dispatch_query(
        GetPostComments(post_id=post_id, limit=limit, offset=offset, db=db)
    )


@post_router.post("/{post_id}/comments", response_model=CommentResponse, status_code=201)
async def create_comment(
    post_id: int, data: CommentCreate,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_session),
):
    return await dispatch_command(
        CreateComment(post_id=post_id, author_id=user_id, content=data.content, db=db)
    )


@post_router.delete("/comments/{comment_id}", status_code=204)
async def delete_comment(
    comment_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_session),
):
    await dispatch_command(DeleteComment(comment_id=comment_id, user_id=user_id, db=db))


# --- Follow ---
follow_router = APIRouter(prefix="/api/follow", tags=["follow"])


@follow_router.post("/{following_id}")
async def follow_user(
    following_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_session),
):
    return await dispatch_command(
        FollowUser(follower_id=user_id, following_id=following_id, db=db)
    )


@follow_router.delete("/{following_id}")
async def unfollow_user(
    following_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_session),
):
    return await dispatch_command(
        UnfollowUser(follower_id=user_id, following_id=following_id, db=db)
    )


# --- Feed ---
feed_router = APIRouter(prefix="/api/feed", tags=["feed"])


@feed_router.get("", response_model=list[PostResponse])
async def get_feed(
    limit: int = 20, offset: int = 0,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_session),
):
    return await dispatch_query(
        GetFeed(user_id=user_id, limit=limit, offset=offset, db=db)
    )


# --- Stories ---
story_router = APIRouter(prefix="/api/stories", tags=["stories"])


@story_router.post("", response_model=StoryResponse, status_code=201)
async def create_story(
    data: StoryCreate,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_session),
):
    return await dispatch_command(
        CreateStory(author_id=user_id, image_url=data.image_url, content=data.content, db=db)
    )


@story_router.get("", response_model=list[StoryResponse])
async def get_my_stories(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_session),
):
    return await dispatch_query(GetMyStories(user_id=user_id, db=db))


@story_router.get("/feed", response_model=list[StoryResponse])
async def get_story_feed(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_session),
):
    return await dispatch_query(GetStoryFeed(user_id=user_id, db=db))


@story_router.delete("/{story_id}", status_code=204)
async def delete_story(
    story_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_session),
):
    await dispatch_command(DeleteStory(story_id=story_id, user_id=user_id, db=db))


# --- Messages ---
message_router = APIRouter(prefix="/api/messages", tags=["messages"])


@message_router.post("", response_model=MessageResponse, status_code=201)
async def send_message(
    data: MessageCreate,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_session),
):
    return await dispatch_command(
        SendMessage(sender_id=user_id, receiver_id=data.receiver_id, content=data.content, db=db)
    )


@message_router.get("", response_model=list[ConversationResponse])
async def list_conversations(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_session),
):
    return await dispatch_query(GetConversations(user_id=user_id, db=db))


@message_router.get("/{other_user_id}", response_model=list[MessageResponse])
async def get_conversation(
    other_user_id: int, limit: int = 50, offset: int = 0,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_session),
):
    return await dispatch_query(
        GetConversation(user_id=user_id, other_user_id=other_user_id, limit=limit, offset=offset, db=db)
    )


@message_router.post("/{sender_id}/read")
async def mark_read(
    sender_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_session),
):
    return await dispatch_command(
        MarkMessagesRead(user_id=user_id, sender_id=sender_id, db=db)
    )


# --- Notifications ---
notification_router = APIRouter(prefix="/api/notifications", tags=["notifications"])


@notification_router.get("", response_model=list[NotificationResponse])
async def list_notifications(
    limit: int = 50, offset: int = 0,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_session),
):
    return await dispatch_query(
        GetNotifications(user_id=user_id, limit=limit, offset=offset, db=db)
    )


@notification_router.post("/{notification_id}/read")
async def mark_notification_read(
    notification_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_session),
):
    return await dispatch_command(
        MarkNotificationRead(notification_id=notification_id, user_id=user_id, db=db)
    )


@notification_router.post("/read-all")
async def mark_all_read(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_session),
):
    return await dispatch_command(
        MarkAllNotificationsRead(user_id=user_id, db=db)
    )


# --- Search ---
search_router = APIRouter(prefix="/api/search", tags=["search"])


@search_router.get("/users", response_model=list[UserResponse])
async def search_users(q: str, limit: int = 20, db: AsyncSession = Depends(get_session)):
    return await dispatch_query(SearchUsers(query=q, limit=limit, db=db))


@search_router.get("/hashtags", response_model=list[HashtagResponse])
async def search_hashtags(q: str, limit: int = 20, db: AsyncSession = Depends(get_session)):
    return await dispatch_query(SearchHashtags(query=q, limit=limit, db=db))


@search_router.get("/posts/hashtag/{tag}", response_model=list[PostResponse])
async def get_posts_by_hashtag(
    tag: str, limit: int = 20, offset: int = 0,
    db: AsyncSession = Depends(get_session),
):
    return await dispatch_query(
        GetPostsByHashtag(tag=tag, limit=limit, offset=offset, db=db)
    )
