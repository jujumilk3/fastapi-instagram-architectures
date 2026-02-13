from datetime import datetime

from pydantic import BaseModel


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


class CommentCreate(BaseModel):
    content: str


class CommentResponse(BaseModel):
    id: int
    post_id: int
    author_id: int
    author_username: str | None = None
    content: str
    created_at: datetime
