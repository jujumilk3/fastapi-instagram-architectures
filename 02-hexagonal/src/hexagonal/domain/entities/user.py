from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class User:
    id: int | None = None
    username: str = ""
    email: str = ""
    hashed_password: str = ""
    full_name: str | None = None
    bio: str | None = None
    profile_image_url: str | None = None
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime | None = None
