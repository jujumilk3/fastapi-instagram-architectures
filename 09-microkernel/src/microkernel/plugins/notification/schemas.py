from datetime import datetime

from pydantic import BaseModel


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
