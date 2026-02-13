from datetime import datetime

from pydantic import BaseModel, EmailStr


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
