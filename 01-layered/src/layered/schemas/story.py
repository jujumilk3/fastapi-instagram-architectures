from datetime import datetime

from pydantic import BaseModel


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
