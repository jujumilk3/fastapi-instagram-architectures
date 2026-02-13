from fastapi import APIRouter, Depends

from hexagonal.adapters.inbound.api.dependencies import (
    get_auth_service, get_comment_service, get_current_user_id, get_feed_service,
    get_follow_service, get_like_service, get_message_service, get_notification_service,
    get_post_service, get_search_service, get_story_service, get_user_service,
)
from hexagonal.adapters.inbound.api.schemas import (
    CommentCreate, CommentResponse, ConversationResponse, HashtagResponse,
    LoginRequest, MessageCreate, MessageResponse, NotificationResponse,
    PostCreate, PostResponse, StoryCreate, StoryResponse, TokenResponse,
    UserCreate, UserProfileResponse, UserResponse, UserUpdate,
)
from hexagonal.application.auth_service import (
    AuthService, CommentService, FeedService, FollowService, LikeService,
    MessageService, NotificationService, PostService, SearchService, StoryService, UserService,
)
from hexagonal.domain.entities.user import User


def _user_to_response(u: User) -> UserResponse:
    return UserResponse(id=u.id, username=u.username, email=u.email, full_name=u.full_name,
                        bio=u.bio, profile_image_url=u.profile_image_url, is_active=u.is_active, created_at=u.created_at)


# --- Auth ---
auth_router = APIRouter(prefix="/api/auth", tags=["auth"])

@auth_router.post("/register", response_model=UserResponse, status_code=201)
async def register(data: UserCreate, svc: AuthService = Depends(get_auth_service)):
    return _user_to_response(await svc.register(data.username, data.email, data.password, data.full_name))

@auth_router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, svc: AuthService = Depends(get_auth_service)):
    token = await svc.login(data.email, data.password)
    return TokenResponse(access_token=token)

@auth_router.get("/me", response_model=UserResponse)
async def me(user_id: int = Depends(get_current_user_id), svc: AuthService = Depends(get_auth_service)):
    return _user_to_response(await svc.get_me(user_id))

# --- Users ---
user_router = APIRouter(prefix="/api/users", tags=["users"])

@user_router.get("/{user_id}", response_model=UserProfileResponse)
async def get_user(user_id: int, svc: UserService = Depends(get_user_service)):
    return await svc.get_profile(user_id)

@user_router.put("/me", response_model=UserResponse)
async def update_me(data: UserUpdate, user_id: int = Depends(get_current_user_id), svc: UserService = Depends(get_user_service)):
    return _user_to_response(await svc.update_me(user_id, **data.model_dump(exclude_unset=True)))

@user_router.get("/{user_id}/posts", response_model=list[PostResponse])
async def get_user_posts(user_id: int, limit: int = 20, offset: int = 0, svc: PostService = Depends(get_post_service)):
    return await svc.get_by_author(user_id, limit, offset)

@user_router.get("/{user_id}/followers", response_model=list[UserResponse])
async def get_followers(user_id: int, svc: UserService = Depends(get_user_service)):
    return [_user_to_response(u) for u in await svc.get_followers(user_id)]

@user_router.get("/{user_id}/following", response_model=list[UserResponse])
async def get_following(user_id: int, svc: UserService = Depends(get_user_service)):
    return [_user_to_response(u) for u in await svc.get_following(user_id)]

# --- Posts ---
post_router = APIRouter(prefix="/api/posts", tags=["posts"])

@post_router.post("", response_model=PostResponse, status_code=201)
async def create_post(data: PostCreate, user_id: int = Depends(get_current_user_id), svc: PostService = Depends(get_post_service)):
    return await svc.create(user_id, data.content, data.image_url)

@post_router.get("/{post_id}", response_model=PostResponse)
async def get_post(post_id: int, svc: PostService = Depends(get_post_service)):
    return await svc.get(post_id)

@post_router.delete("/{post_id}", status_code=204)
async def delete_post(post_id: int, user_id: int = Depends(get_current_user_id), svc: PostService = Depends(get_post_service)):
    await svc.delete(post_id, user_id)

@post_router.post("/{post_id}/likes")
async def toggle_like(post_id: int, user_id: int = Depends(get_current_user_id), svc: LikeService = Depends(get_like_service)):
    return await svc.toggle(post_id, user_id)

@post_router.get("/{post_id}/comments", response_model=list[CommentResponse])
async def get_comments(post_id: int, limit: int = 50, offset: int = 0, svc: CommentService = Depends(get_comment_service)):
    return await svc.get_by_post(post_id, limit, offset)

@post_router.post("/{post_id}/comments", response_model=CommentResponse, status_code=201)
async def create_comment(post_id: int, data: CommentCreate, user_id: int = Depends(get_current_user_id), svc: CommentService = Depends(get_comment_service)):
    return await svc.create(post_id, user_id, data.content)

@post_router.delete("/comments/{comment_id}", status_code=204)
async def delete_comment(comment_id: int, user_id: int = Depends(get_current_user_id), svc: CommentService = Depends(get_comment_service)):
    await svc.delete(comment_id, user_id)

# --- Follow ---
follow_router = APIRouter(prefix="/api/follow", tags=["follow"])

@follow_router.post("/{following_id}")
async def follow_user(following_id: int, user_id: int = Depends(get_current_user_id), svc: FollowService = Depends(get_follow_service)):
    return await svc.follow(user_id, following_id)

@follow_router.delete("/{following_id}")
async def unfollow_user(following_id: int, user_id: int = Depends(get_current_user_id), svc: FollowService = Depends(get_follow_service)):
    return await svc.unfollow(user_id, following_id)

# --- Feed ---
feed_router = APIRouter(prefix="/api/feed", tags=["feed"])

@feed_router.get("", response_model=list[PostResponse])
async def get_feed(limit: int = 20, offset: int = 0, user_id: int = Depends(get_current_user_id), svc: FeedService = Depends(get_feed_service)):
    return await svc.get_feed(user_id, limit, offset)

# --- Stories ---
story_router = APIRouter(prefix="/api/stories", tags=["stories"])

@story_router.post("", response_model=StoryResponse, status_code=201)
async def create_story(data: StoryCreate, user_id: int = Depends(get_current_user_id), svc: StoryService = Depends(get_story_service)):
    return await svc.create(user_id, data.image_url, data.content)

@story_router.get("", response_model=list[StoryResponse])
async def get_my_stories(user_id: int = Depends(get_current_user_id), svc: StoryService = Depends(get_story_service)):
    return await svc.get_my_stories(user_id)

@story_router.get("/feed", response_model=list[StoryResponse])
async def get_story_feed(user_id: int = Depends(get_current_user_id), svc: StoryService = Depends(get_story_service)):
    return await svc.get_feed(user_id)

@story_router.delete("/{story_id}", status_code=204)
async def delete_story(story_id: int, user_id: int = Depends(get_current_user_id), svc: StoryService = Depends(get_story_service)):
    await svc.delete(story_id, user_id)

# --- Messages ---
message_router = APIRouter(prefix="/api/messages", tags=["messages"])

@message_router.post("", response_model=MessageResponse, status_code=201)
async def send_message(data: MessageCreate, user_id: int = Depends(get_current_user_id), svc: MessageService = Depends(get_message_service)):
    m = await svc.send(user_id, data.receiver_id, data.content)
    return MessageResponse(id=m.id, sender_id=m.sender_id, receiver_id=m.receiver_id, content=m.content, is_read=m.is_read, created_at=m.created_at)

@message_router.get("", response_model=list[ConversationResponse])
async def list_conversations(user_id: int = Depends(get_current_user_id), svc: MessageService = Depends(get_message_service)):
    convos = await svc.get_conversations(user_id)
    return [ConversationResponse(other_user_id=c["other_user_id"], last_message=MessageResponse(
        id=c["last_message"].id, sender_id=c["last_message"].sender_id, receiver_id=c["last_message"].receiver_id,
        content=c["last_message"].content, is_read=c["last_message"].is_read, created_at=c["last_message"].created_at
    )) for c in convos]

@message_router.get("/{other_user_id}", response_model=list[MessageResponse])
async def get_conversation(other_user_id: int, limit: int = 50, offset: int = 0, user_id: int = Depends(get_current_user_id), svc: MessageService = Depends(get_message_service)):
    msgs = await svc.get_conversation(user_id, other_user_id, limit, offset)
    return [MessageResponse(id=m.id, sender_id=m.sender_id, receiver_id=m.receiver_id, content=m.content, is_read=m.is_read, created_at=m.created_at) for m in msgs]

@message_router.post("/{sender_id}/read")
async def mark_read(sender_id: int, user_id: int = Depends(get_current_user_id), svc: MessageService = Depends(get_message_service)):
    return await svc.mark_read(user_id, sender_id)

# --- Notifications ---
notification_router = APIRouter(prefix="/api/notifications", tags=["notifications"])

@notification_router.get("", response_model=list[NotificationResponse])
async def list_notifications(limit: int = 50, offset: int = 0, user_id: int = Depends(get_current_user_id), svc: NotificationService = Depends(get_notification_service)):
    nots = await svc.get_notifications(user_id, limit, offset)
    return [NotificationResponse(id=n.id, user_id=n.user_id, actor_id=n.actor_id, type=n.type,
            reference_id=n.reference_id, message=n.message, is_read=n.is_read, created_at=n.created_at) for n in nots]

@notification_router.post("/{notification_id}/read")
async def mark_notification_read(notification_id: int, user_id: int = Depends(get_current_user_id), svc: NotificationService = Depends(get_notification_service)):
    return await svc.mark_read(notification_id, user_id)

@notification_router.post("/read-all")
async def mark_all_read(user_id: int = Depends(get_current_user_id), svc: NotificationService = Depends(get_notification_service)):
    return await svc.mark_all_read(user_id)

# --- Search ---
search_router = APIRouter(prefix="/api/search", tags=["search"])

@search_router.get("/users", response_model=list[UserResponse])
async def search_users(q: str, limit: int = 20, svc: SearchService = Depends(get_search_service)):
    return [_user_to_response(u) for u in await svc.search_users(q, limit)]

@search_router.get("/hashtags", response_model=list[HashtagResponse])
async def search_hashtags(q: str, limit: int = 20, svc: SearchService = Depends(get_search_service)):
    hs = await svc.search_hashtags(q, limit)
    return [HashtagResponse(id=h.id, name=h.name) for h in hs]

@search_router.get("/posts/hashtag/{tag}", response_model=list[PostResponse])
async def get_posts_by_hashtag(tag: str, limit: int = 20, offset: int = 0, svc: SearchService = Depends(get_search_service)):
    return await svc.get_posts_by_hashtag(tag, limit, offset)
