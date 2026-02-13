from datetime import datetime, timedelta, timezone

from functional_core.core.types import Result

STORY_EXPIRY_HOURS = 24


def validate_story(image_url: str | None, content: str | None) -> Result:
    if not image_url and not content:
        return Result(success=False, error="Story must have image or content")
    return Result(success=True)


def is_story_expired(created_at: datetime) -> bool:
    cutoff = datetime.now(timezone.utc) - timedelta(hours=STORY_EXPIRY_HOURS)
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)
    return created_at < cutoff


def get_story_cutoff() -> datetime:
    return datetime.now(timezone.utc) - timedelta(hours=STORY_EXPIRY_HOURS)
