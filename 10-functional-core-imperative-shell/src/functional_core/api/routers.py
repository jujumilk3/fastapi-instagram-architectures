from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from functional_core.api.dependencies import get_current_user_id
from functional_core.api.schemas import (
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
from functional_core.shell.database import get_db
from functional_core.shell.handlers import (
    auth_handler,
    comment_handler,
    feed_handler,
    follow_handler,
    like_handler,
    message_handler,
    notification_handler,
    post_handler,
    search_handler,
    story_handler,
    user_handler,
)

# --- Auth ---

auth_router = APIRouter(prefix="/api/auth", tags=["auth"])


@auth_router.post("/register", response_model=UserResponse, status_code=201)
async def register(data: UserCreate, db: AsyncSession = Depends(get_db)):
    user = await auth_handler.register_user(
        db, data.username, data.email, data.password, data.full_name
    )
    return UserResponse.model_validate(user)


@auth_router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    return await auth_handler.login_user(db, data.email, data.password)


@auth_router.get("/me", response_model=UserResponse)
async def me(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await auth_handler.get_current_user(db, user_id)
    return UserResponse.model_validate(user)


# --- Users ---

user_router = APIRouter(prefix="/api/users", tags=["users"])


@user_router.get("/{user_id}", response_model=UserProfileResponse)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    return await user_handler.get_profile(db, user_id)


@user_router.put("/me", response_model=UserResponse)
async def update_me(
    data: UserUpdate,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await user_handler.update_profile(db, user_id, data.model_dump(exclude_unset=True))
    return UserResponse.model_validate(user)


@user_router.get("/{user_id}/posts", response_model=list[PostResponse])
async def get_user_posts(
    user_id: int, limit: int = 20, offset: int = 0, db: AsyncSession = Depends(get_db)
):
    return await post_handler.get_posts_by_author(db, user_id, limit, offset)


@user_router.get("/{user_id}/followers", response_model=list[UserResponse])
async def get_followers(user_id: int, db: AsyncSession = Depends(get_db)):
    users = await user_handler.get_followers(db, user_id)
    return [UserResponse.model_validate(u) for u in users]


@user_router.get("/{user_id}/following", response_model=list[UserResponse])
async def get_following(user_id: int, db: AsyncSession = Depends(get_db)):
    users = await user_handler.get_following(db, user_id)
    return [UserResponse.model_validate(u) for u in users]


# --- Posts ---

post_router = APIRouter(prefix="/api/posts", tags=["posts"])


@post_router.post("", response_model=PostResponse, status_code=201)
async def create_post(
    data: PostCreate,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    return await post_handler.create_post(db, user_id, data.content, data.image_url)


@post_router.get("/{post_id}", response_model=PostResponse)
async def get_post(post_id: int, db: AsyncSession = Depends(get_db)):
    return await post_handler.get_post(db, post_id)


@post_router.delete("/{post_id}", status_code=204)
async def delete_post(
    post_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    await post_handler.delete_post(db, post_id, user_id)


@post_router.post("/{post_id}/likes")
async def toggle_like(
    post_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    return await like_handler.toggle_like(db, post_id, user_id)


@post_router.get("/{post_id}/comments", response_model=list[CommentResponse])
async def get_comments(
    post_id: int, limit: int = 50, offset: int = 0, db: AsyncSession = Depends(get_db)
):
    comments = await comment_handler.get_comments_by_post(db, post_id, limit, offset)
    return [
        CommentResponse(
            id=c.id,
            post_id=c.post_id,
            author_id=c.author_id,
            author_username=c.author.username if c.author else None,
            content=c.content,
            created_at=c.created_at,
        )
        for c in comments
    ]


@post_router.post("/{post_id}/comments", response_model=CommentResponse, status_code=201)
async def create_comment(
    post_id: int,
    data: CommentCreate,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    comment = await comment_handler.create_comment(db, post_id, user_id, data.content)
    return CommentResponse(
        id=comment.id,
        post_id=comment.post_id,
        author_id=comment.author_id,
        content=comment.content,
        created_at=comment.created_at,
    )


@post_router.delete("/comments/{comment_id}", status_code=204)
async def delete_comment(
    comment_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    await comment_handler.delete_comment(db, comment_id, user_id)


# --- Follow ---

follow_router = APIRouter(prefix="/api/follow", tags=["follow"])


@follow_router.post("/{following_id}")
async def follow_user(
    following_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    return await follow_handler.follow_user(db, user_id, following_id)


@follow_router.delete("/{following_id}")
async def unfollow_user(
    following_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    return await follow_handler.unfollow_user(db, user_id, following_id)


# --- Feed ---

feed_router = APIRouter(prefix="/api/feed", tags=["feed"])


@feed_router.get("", response_model=list[PostResponse])
async def get_feed(
    limit: int = 20,
    offset: int = 0,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    return await feed_handler.get_feed(db, user_id, limit, offset)


# --- Stories ---

story_router = APIRouter(prefix="/api/stories", tags=["stories"])


@story_router.post("", response_model=StoryResponse, status_code=201)
async def create_story(
    data: StoryCreate,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    story = await story_handler.create_story(db, user_id, data.image_url, data.content)
    return StoryResponse(
        id=story.id,
        author_id=story.author_id,
        image_url=story.image_url,
        content=story.content,
        created_at=story.created_at,
    )


@story_router.get("", response_model=list[StoryResponse])
async def get_my_stories(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    stories = await story_handler.get_my_stories(db, user_id)
    return [
        StoryResponse(
            id=s.id,
            author_id=s.author_id,
            author_username=s.author.username if s.author else None,
            image_url=s.image_url,
            content=s.content,
            created_at=s.created_at,
        )
        for s in stories
    ]


@story_router.get("/feed", response_model=list[StoryResponse])
async def get_story_feed(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    stories = await story_handler.get_story_feed(db, user_id)
    return [
        StoryResponse(
            id=s.id,
            author_id=s.author_id,
            author_username=s.author.username if s.author else None,
            image_url=s.image_url,
            content=s.content,
            created_at=s.created_at,
        )
        for s in stories
    ]


@story_router.delete("/{story_id}", status_code=204)
async def delete_story(
    story_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    await story_handler.delete_story(db, story_id, user_id)


# --- Messages ---

message_router = APIRouter(prefix="/api/messages", tags=["messages"])


@message_router.post("", response_model=MessageResponse, status_code=201)
async def send_message(
    data: MessageCreate,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    msg = await message_handler.send_message(db, user_id, data.receiver_id, data.content)
    return MessageResponse.model_validate(msg)


@message_router.get("", response_model=list[ConversationResponse])
async def list_conversations(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    convos = await message_handler.get_conversations(db, user_id)
    return [
        ConversationResponse(
            other_user_id=c["other_user_id"],
            last_message=MessageResponse.model_validate(c["last_message"]),
        )
        for c in convos
    ]


@message_router.get("/{other_user_id}", response_model=list[MessageResponse])
async def get_conversation(
    other_user_id: int,
    limit: int = 50,
    offset: int = 0,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    messages = await message_handler.get_conversation(db, user_id, other_user_id, limit, offset)
    return [MessageResponse.model_validate(m) for m in messages]


@message_router.post("/{sender_id}/read")
async def mark_read(
    sender_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    return await message_handler.mark_messages_read(db, user_id, sender_id)


# --- Notifications ---

notification_router = APIRouter(prefix="/api/notifications", tags=["notifications"])


@notification_router.get("", response_model=list[NotificationResponse])
async def list_notifications(
    limit: int = 50,
    offset: int = 0,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    notifications = await notification_handler.get_notifications(db, user_id, limit, offset)
    return [NotificationResponse.model_validate(n) for n in notifications]


@notification_router.post("/{notification_id}/read")
async def mark_notification_read(
    notification_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    return await notification_handler.mark_notification_read(db, notification_id, user_id)


@notification_router.post("/read-all")
async def mark_all_read(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    return await notification_handler.mark_all_notifications_read(db, user_id)


# --- Search ---

search_router = APIRouter(prefix="/api/search", tags=["search"])


@search_router.get("/users", response_model=list[UserResponse])
async def search_users(q: str, limit: int = 20, db: AsyncSession = Depends(get_db)):
    users = await search_handler.search_users(db, q, limit)
    return [UserResponse.model_validate(u) for u in users]


@search_router.get("/hashtags", response_model=list[HashtagResponse])
async def search_hashtags(q: str, limit: int = 20, db: AsyncSession = Depends(get_db)):
    hashtags = await search_handler.search_hashtags(db, q, limit)
    return [HashtagResponse.model_validate(h) for h in hashtags]


@search_router.get("/posts/hashtag/{tag}", response_model=list[PostResponse])
async def get_posts_by_hashtag(
    tag: str, limit: int = 20, offset: int = 0, db: AsyncSession = Depends(get_db)
):
    return await search_handler.get_posts_by_hashtag(db, tag, limit, offset)
