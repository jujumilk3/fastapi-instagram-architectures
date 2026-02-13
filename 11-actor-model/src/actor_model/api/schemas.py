from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: str | None = None


class UserUpdate(BaseModel):
    full_name: str | None = None
    bio: str | None = None
    profile_image_url: str | None = None


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    full_name: str | None
    bio: str | None
    profile_image_url: str | None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UserProfileResponse(BaseModel):
    id: int
    username: str
    full_name: str | None
    bio: str | None
    profile_image_url: str | None
    post_count: int = 0
    follower_count: int = 0
    following_count: int = 0

    model_config = {"from_attributes": True}


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class PostCreate(BaseModel):
    content: str | None = None
    image_url: str | None = None


class PostResponse(BaseModel):
    id: int
    author_id: int
    author_username: str | None = None
    content: str | None
    image_url: str | None
    like_count: int = 0
    comment_count: int = 0
    created_at: datetime

    model_config = {"from_attributes": True}


class CommentCreate(BaseModel):
    content: str


class CommentResponse(BaseModel):
    id: int
    post_id: int
    author_id: int
    author_username: str | None = None
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


class StoryCreate(BaseModel):
    image_url: str | None = None
    content: str | None = None


class StoryResponse(BaseModel):
    id: int
    author_id: int
    author_username: str | None = None
    image_url: str | None
    content: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class MessageCreate(BaseModel):
    receiver_id: int
    content: str


class MessageResponse(BaseModel):
    id: int
    sender_id: int
    receiver_id: int
    content: str
    is_read: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class ConversationResponse(BaseModel):
    other_user_id: int
    last_message: MessageResponse


class NotificationResponse(BaseModel):
    id: int
    user_id: int
    actor_id: int
    type: str
    reference_id: int | None
    message: str
    is_read: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class HashtagResponse(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}
