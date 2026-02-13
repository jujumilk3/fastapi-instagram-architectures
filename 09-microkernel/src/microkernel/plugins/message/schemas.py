from datetime import datetime

from pydantic import BaseModel


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
