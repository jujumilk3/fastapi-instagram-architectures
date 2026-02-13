from datetime import datetime, timezone

from cqrs_es.write.events.events import USER_REGISTERED, USER_UPDATED


class UserAggregate:
    def __init__(self) -> None:
        self.id: int | None = None
        self.username: str = ""
        self.email: str = ""
        self.hashed_password: str = ""
        self.full_name: str | None = None
        self.bio: str | None = None
        self.profile_image_url: str | None = None
        self.is_active: bool = True
        self.version: int = 0

    def apply(self, event_type: str, data: dict) -> None:
        if event_type == USER_REGISTERED:
            self.id = data["user_id"]
            self.username = data["username"]
            self.email = data["email"]
            self.hashed_password = data["hashed_password"]
            self.full_name = data.get("full_name")
            self.is_active = True
        elif event_type == USER_UPDATED:
            if "full_name" in data:
                self.full_name = data["full_name"]
            if "bio" in data:
                self.bio = data["bio"]
            if "profile_image_url" in data:
                self.profile_image_url = data["profile_image_url"]
        self.version += 1

    @staticmethod
    def register(user_id: int, username: str, email: str, hashed_password: str,
                 full_name: str | None) -> tuple[str, dict]:
        return USER_REGISTERED, {
            "user_id": user_id,
            "username": username,
            "email": email,
            "hashed_password": hashed_password,
            "full_name": full_name,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

    @staticmethod
    def update(user_id: int, **kwargs: str | None) -> tuple[str, dict]:
        data = {"user_id": user_id}
        for key, val in kwargs.items():
            if val is not None:
                data[key] = val
        return USER_UPDATED, data
