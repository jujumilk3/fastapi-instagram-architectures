from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from ddd.domain.shared.event import ProfileUpdatedEvent, UserRegisteredEvent
from ddd.domain.user.value_objects import Email, Username


@dataclass
class UserAggregate:
    id: int | None = None
    username: Username = field(default_factory=lambda: Username("_"))
    email: Email = field(default_factory=lambda: Email("_@_._"))
    hashed_password: str = ""
    full_name: str | None = None
    bio: str | None = None
    profile_image_url: str | None = None
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime | None = None
    _events: list = field(default_factory=list, repr=False, compare=False)

    @classmethod
    def create(
        cls,
        username: str,
        email: str,
        hashed_password: str,
        full_name: str | None = None,
    ) -> UserAggregate:
        user = cls(
            username=Username(username),
            email=Email(email),
            hashed_password=hashed_password,
            full_name=full_name,
        )
        user._events.append(UserRegisteredEvent(
            user_id=0, username=username, email=email,
        ))
        return user

    @classmethod
    def reconstitute(
        cls,
        id: int,
        username: str,
        email: str,
        hashed_password: str,
        full_name: str | None,
        bio: str | None,
        profile_image_url: str | None,
        is_active: bool,
        created_at: datetime,
        updated_at: datetime | None,
    ) -> UserAggregate:
        return cls(
            id=id,
            username=Username(username),
            email=Email(email),
            hashed_password=hashed_password,
            full_name=full_name,
            bio=bio,
            profile_image_url=profile_image_url,
            is_active=is_active,
            created_at=created_at,
            updated_at=updated_at,
        )

    def update_profile(
        self,
        full_name: str | None = None,
        bio: str | None = None,
        profile_image_url: str | None = None,
    ):
        if full_name is not None:
            self.full_name = full_name
        if bio is not None:
            self.bio = bio
        if profile_image_url is not None:
            self.profile_image_url = profile_image_url
        self._events.append(ProfileUpdatedEvent(user_id=self.id))

    def collect_events(self) -> list:
        events = self._events.copy()
        self._events.clear()
        return events
