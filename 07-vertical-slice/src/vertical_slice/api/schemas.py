from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserCreateBody(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: str | None = None


class LoginBody(BaseModel):
    email: EmailStr
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    full_name: str | None
    bio: str | None
    profile_image_url: str | None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UserProfileOut(BaseModel):
    id: int
    username: str
    full_name: str | None
    bio: str | None
    profile_image_url: str | None
    post_count: int
    follower_count: int
    following_count: int


class UserUpdateBody(BaseModel):
    full_name: str | None = None
    bio: str | None = None
    profile_image_url: str | None = None


class PostCreateBody(BaseModel):
    content: str | None = None
    image_url: str | None = None


class PostOut(BaseModel):
    id: int
    author_id: int
    author_username: str | None = None
    content: str | None
    image_url: str | None
    like_count: int
    comment_count: int
    created_at: datetime


class CommentCreateBody(BaseModel):
    content: str


class CommentOut(BaseModel):
    id: int
    post_id: int
    author_id: int
    author_username: str | None = None
    content: str
    created_at: datetime


class LikeOut(BaseModel):
    liked: bool
    like_count: int


class FollowOut(BaseModel):
    following: bool


class StoryCreateBody(BaseModel):
    image_url: str | None = None
    content: str | None = None


class StoryOut(BaseModel):
    id: int
    author_id: int
    author_username: str | None = None
    image_url: str | None
    content: str | None
    created_at: datetime


class MessageCreateBody(BaseModel):
    receiver_id: int
    content: str


class MessageOut(BaseModel):
    id: int
    sender_id: int
    receiver_id: int
    content: str
    is_read: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class ConversationOut(BaseModel):
    other_user_id: int
    last_message: MessageOut


class NotificationOut(BaseModel):
    id: int
    user_id: int
    actor_id: int
    type: str
    reference_id: int | None
    message: str
    is_read: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class HashtagOut(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


class StatusOut(BaseModel):
    status: str
