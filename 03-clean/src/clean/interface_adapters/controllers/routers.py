from fastapi import APIRouter, Depends

from clean.entities.user import User
from clean.frameworks.dependencies import (
    get_comments_uc, get_conversation_uc, get_conversations_uc,
    get_create_comment_uc, get_create_post_uc, get_create_story_uc,
    get_current_user_id, get_delete_comment_uc, get_delete_post_uc,
    get_delete_story_uc, get_feed_uc, get_follow_user_uc, get_followers_uc,
    get_following_uc, get_get_post_uc, get_login_uc, get_mark_all_notifications_read_uc,
    get_mark_messages_read_uc, get_mark_notification_read_uc, get_me_uc,
    get_my_stories_uc, get_notifications_uc, get_posts_by_hashtag_uc,
    get_profile_uc, get_register_uc, get_search_hashtags_uc, get_search_users_uc,
    get_send_message_uc, get_story_feed_uc, get_toggle_like_uc, get_unfollow_user_uc,
    get_update_profile_uc, get_user_posts_uc,
)
from clean.interface_adapters.schemas.schemas import (
    CommentCreate, CommentResponse, ConversationResponse, HashtagResponse,
    LoginRequest, MessageCreate, MessageResponse, NotificationResponse,
    PostCreate, PostResponse, StoryCreate, StoryResponse, TokenResponse,
    UserCreate, UserProfileResponse, UserResponse, UserUpdate,
)
from clean.use_cases.auth.get_me import GetMeUseCase
from clean.use_cases.auth.login import LoginUseCase
from clean.use_cases.auth.register import RegisterUseCase
from clean.use_cases.comment.create_comment import CreateCommentUseCase
from clean.use_cases.comment.delete_comment import DeleteCommentUseCase
from clean.use_cases.comment.get_comments import GetCommentsUseCase
from clean.use_cases.feed.get_feed import GetFeedUseCase
from clean.use_cases.follow.follow_user import FollowUserUseCase
from clean.use_cases.follow.unfollow_user import UnfollowUserUseCase
from clean.use_cases.like.toggle_like import ToggleLikeUseCase
from clean.use_cases.message.get_conversation import GetConversationUseCase
from clean.use_cases.message.get_conversations import GetConversationsUseCase
from clean.use_cases.message.mark_read import MarkMessagesReadUseCase
from clean.use_cases.message.send_message import SendMessageUseCase
from clean.use_cases.notification.get_notifications import GetNotificationsUseCase
from clean.use_cases.notification.mark_all_read import MarkAllNotificationsReadUseCase
from clean.use_cases.notification.mark_read import MarkNotificationReadUseCase
from clean.use_cases.post.create_post import CreatePostUseCase
from clean.use_cases.post.delete_post import DeletePostUseCase
from clean.use_cases.post.get_post import GetPostUseCase
from clean.use_cases.post.get_user_posts import GetUserPostsUseCase
from clean.use_cases.search.get_posts_by_hashtag import GetPostsByHashtagUseCase
from clean.use_cases.search.search_hashtags import SearchHashtagsUseCase
from clean.use_cases.search.search_users import SearchUsersUseCase
from clean.use_cases.story.create_story import CreateStoryUseCase
from clean.use_cases.story.delete_story import DeleteStoryUseCase
from clean.use_cases.story.get_my_stories import GetMyStoriesUseCase
from clean.use_cases.story.get_story_feed import GetStoryFeedUseCase
from clean.use_cases.user.get_followers import GetFollowersUseCase
from clean.use_cases.user.get_following import GetFollowingUseCase
from clean.use_cases.user.get_profile import GetProfileUseCase
from clean.use_cases.user.update_profile import UpdateProfileUseCase


def _user_to_response(u: User) -> UserResponse:
    return UserResponse(
        id=u.id, username=u.username, email=u.email, full_name=u.full_name,
        bio=u.bio, profile_image_url=u.profile_image_url, is_active=u.is_active, created_at=u.created_at,
    )


# --- Auth ---
auth_router = APIRouter(prefix="/api/auth", tags=["auth"])

@auth_router.post("/register", response_model=UserResponse, status_code=201)
async def register(data: UserCreate, uc: RegisterUseCase = Depends(get_register_uc)):
    return _user_to_response(await uc.execute(data.username, data.email, data.password, data.full_name))

@auth_router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, uc: LoginUseCase = Depends(get_login_uc)):
    token = await uc.execute(data.email, data.password)
    return TokenResponse(access_token=token)

@auth_router.get("/me", response_model=UserResponse)
async def me(user_id: int = Depends(get_current_user_id), uc: GetMeUseCase = Depends(get_me_uc)):
    return _user_to_response(await uc.execute(user_id))


# --- Users ---
user_router = APIRouter(prefix="/api/users", tags=["users"])

@user_router.get("/{user_id}", response_model=UserProfileResponse)
async def get_user(user_id: int, uc: GetProfileUseCase = Depends(get_profile_uc)):
    return await uc.execute(user_id)

@user_router.put("/me", response_model=UserResponse)
async def update_me(data: UserUpdate, user_id: int = Depends(get_current_user_id), uc: UpdateProfileUseCase = Depends(get_update_profile_uc)):
    return _user_to_response(await uc.execute(user_id, **data.model_dump(exclude_unset=True)))

@user_router.get("/{user_id}/posts", response_model=list[PostResponse])
async def get_user_posts(user_id: int, limit: int = 20, offset: int = 0, uc: GetUserPostsUseCase = Depends(get_user_posts_uc)):
    return await uc.execute(user_id, limit, offset)

@user_router.get("/{user_id}/followers", response_model=list[UserResponse])
async def get_followers(user_id: int, uc: GetFollowersUseCase = Depends(get_followers_uc)):
    return [_user_to_response(u) for u in await uc.execute(user_id)]

@user_router.get("/{user_id}/following", response_model=list[UserResponse])
async def get_following(user_id: int, uc: GetFollowingUseCase = Depends(get_following_uc)):
    return [_user_to_response(u) for u in await uc.execute(user_id)]


# --- Posts ---
post_router = APIRouter(prefix="/api/posts", tags=["posts"])

@post_router.post("", response_model=PostResponse, status_code=201)
async def create_post(data: PostCreate, user_id: int = Depends(get_current_user_id), uc: CreatePostUseCase = Depends(get_create_post_uc)):
    return await uc.execute(user_id, data.content, data.image_url)

@post_router.get("/{post_id}", response_model=PostResponse)
async def get_post(post_id: int, uc: GetPostUseCase = Depends(get_get_post_uc)):
    return await uc.execute(post_id)

@post_router.delete("/{post_id}", status_code=204)
async def delete_post(post_id: int, user_id: int = Depends(get_current_user_id), uc: DeletePostUseCase = Depends(get_delete_post_uc)):
    await uc.execute(post_id, user_id)

@post_router.post("/{post_id}/likes")
async def toggle_like(post_id: int, user_id: int = Depends(get_current_user_id), uc: ToggleLikeUseCase = Depends(get_toggle_like_uc)):
    return await uc.execute(post_id, user_id)

@post_router.get("/{post_id}/comments", response_model=list[CommentResponse])
async def get_comments(post_id: int, limit: int = 50, offset: int = 0, uc: GetCommentsUseCase = Depends(get_comments_uc)):
    return await uc.execute(post_id, limit, offset)

@post_router.post("/{post_id}/comments", response_model=CommentResponse, status_code=201)
async def create_comment(post_id: int, data: CommentCreate, user_id: int = Depends(get_current_user_id), uc: CreateCommentUseCase = Depends(get_create_comment_uc)):
    return await uc.execute(post_id, user_id, data.content)

@post_router.delete("/comments/{comment_id}", status_code=204)
async def delete_comment(comment_id: int, user_id: int = Depends(get_current_user_id), uc: DeleteCommentUseCase = Depends(get_delete_comment_uc)):
    await uc.execute(comment_id, user_id)


# --- Follow ---
follow_router = APIRouter(prefix="/api/follow", tags=["follow"])

@follow_router.post("/{following_id}")
async def follow_user(following_id: int, user_id: int = Depends(get_current_user_id), uc: FollowUserUseCase = Depends(get_follow_user_uc)):
    return await uc.execute(user_id, following_id)

@follow_router.delete("/{following_id}")
async def unfollow_user(following_id: int, user_id: int = Depends(get_current_user_id), uc: UnfollowUserUseCase = Depends(get_unfollow_user_uc)):
    return await uc.execute(user_id, following_id)


# --- Feed ---
feed_router = APIRouter(prefix="/api/feed", tags=["feed"])

@feed_router.get("", response_model=list[PostResponse])
async def get_feed(limit: int = 20, offset: int = 0, user_id: int = Depends(get_current_user_id), uc: GetFeedUseCase = Depends(get_feed_uc)):
    return await uc.execute(user_id, limit, offset)


# --- Stories ---
story_router = APIRouter(prefix="/api/stories", tags=["stories"])

@story_router.post("", response_model=StoryResponse, status_code=201)
async def create_story(data: StoryCreate, user_id: int = Depends(get_current_user_id), uc: CreateStoryUseCase = Depends(get_create_story_uc)):
    return await uc.execute(user_id, data.image_url, data.content)

@story_router.get("", response_model=list[StoryResponse])
async def get_my_stories(user_id: int = Depends(get_current_user_id), uc: GetMyStoriesUseCase = Depends(get_my_stories_uc)):
    return await uc.execute(user_id)

@story_router.get("/feed", response_model=list[StoryResponse])
async def get_story_feed(user_id: int = Depends(get_current_user_id), uc: GetStoryFeedUseCase = Depends(get_story_feed_uc)):
    return await uc.execute(user_id)

@story_router.delete("/{story_id}", status_code=204)
async def delete_story(story_id: int, user_id: int = Depends(get_current_user_id), uc: DeleteStoryUseCase = Depends(get_delete_story_uc)):
    await uc.execute(story_id, user_id)


# --- Messages ---
message_router = APIRouter(prefix="/api/messages", tags=["messages"])

@message_router.post("", response_model=MessageResponse, status_code=201)
async def send_message(data: MessageCreate, user_id: int = Depends(get_current_user_id), uc: SendMessageUseCase = Depends(get_send_message_uc)):
    m = await uc.execute(user_id, data.receiver_id, data.content)
    return MessageResponse(id=m.id, sender_id=m.sender_id, receiver_id=m.receiver_id, content=m.content, is_read=m.is_read, created_at=m.created_at)

@message_router.get("", response_model=list[ConversationResponse])
async def list_conversations(user_id: int = Depends(get_current_user_id), uc: GetConversationsUseCase = Depends(get_conversations_uc)):
    convos = await uc.execute(user_id)
    return [ConversationResponse(other_user_id=c["other_user_id"], last_message=MessageResponse(
        id=c["last_message"].id, sender_id=c["last_message"].sender_id, receiver_id=c["last_message"].receiver_id,
        content=c["last_message"].content, is_read=c["last_message"].is_read, created_at=c["last_message"].created_at,
    )) for c in convos]

@message_router.get("/{other_user_id}", response_model=list[MessageResponse])
async def get_conversation(other_user_id: int, limit: int = 50, offset: int = 0, user_id: int = Depends(get_current_user_id), uc: GetConversationUseCase = Depends(get_conversation_uc)):
    msgs = await uc.execute(user_id, other_user_id, limit, offset)
    return [MessageResponse(id=m.id, sender_id=m.sender_id, receiver_id=m.receiver_id, content=m.content, is_read=m.is_read, created_at=m.created_at) for m in msgs]

@message_router.post("/{sender_id}/read")
async def mark_read(sender_id: int, user_id: int = Depends(get_current_user_id), uc: MarkMessagesReadUseCase = Depends(get_mark_messages_read_uc)):
    return await uc.execute(user_id, sender_id)


# --- Notifications ---
notification_router = APIRouter(prefix="/api/notifications", tags=["notifications"])

@notification_router.get("", response_model=list[NotificationResponse])
async def list_notifications(limit: int = 50, offset: int = 0, user_id: int = Depends(get_current_user_id), uc: GetNotificationsUseCase = Depends(get_notifications_uc)):
    nots = await uc.execute(user_id, limit, offset)
    return [NotificationResponse(id=n.id, user_id=n.user_id, actor_id=n.actor_id, type=n.type,
            reference_id=n.reference_id, message=n.message, is_read=n.is_read, created_at=n.created_at) for n in nots]

@notification_router.post("/{notification_id}/read")
async def mark_notification_read(notification_id: int, user_id: int = Depends(get_current_user_id), uc: MarkNotificationReadUseCase = Depends(get_mark_notification_read_uc)):
    return await uc.execute(notification_id, user_id)

@notification_router.post("/read-all")
async def mark_all_read(user_id: int = Depends(get_current_user_id), uc: MarkAllNotificationsReadUseCase = Depends(get_mark_all_notifications_read_uc)):
    return await uc.execute(user_id)


# --- Search ---
search_router = APIRouter(prefix="/api/search", tags=["search"])

@search_router.get("/users", response_model=list[UserResponse])
async def search_users(q: str, limit: int = 20, uc: SearchUsersUseCase = Depends(get_search_users_uc)):
    return [_user_to_response(u) for u in await uc.execute(q, limit)]

@search_router.get("/hashtags", response_model=list[HashtagResponse])
async def search_hashtags(q: str, limit: int = 20, uc: SearchHashtagsUseCase = Depends(get_search_hashtags_uc)):
    hs = await uc.execute(q, limit)
    return [HashtagResponse(id=h.id, name=h.name) for h in hs]

@search_router.get("/posts/hashtag/{tag}", response_model=list[PostResponse])
async def get_posts_by_hashtag(tag: str, limit: int = 20, offset: int = 0, uc: GetPostsByHashtagUseCase = Depends(get_posts_by_hashtag_uc)):
    return await uc.execute(tag, limit, offset)
