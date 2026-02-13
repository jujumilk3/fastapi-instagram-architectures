import re

from functional_core.core.types import Result


def validate_post(content: str | None, image_url: str | None) -> Result:
    if not content and not image_url:
        return Result(success=False, error="Post must have content or image")
    return Result(success=True)


def extract_hashtags(content: str | None) -> list[str]:
    if not content:
        return []
    return re.findall(r"#(\w+)", content)


def can_delete_post(post_owner_id: int, requester_id: int) -> bool:
    return post_owner_id == requester_id


def build_post_response(
    post_id: int,
    author_id: int,
    author_username: str | None,
    content: str | None,
    image_url: str | None,
    like_count: int,
    comment_count: int,
    created_at: object,
) -> dict:
    return {
        "id": post_id,
        "author_id": author_id,
        "author_username": author_username,
        "content": content,
        "image_url": image_url,
        "like_count": like_count,
        "comment_count": comment_count,
        "created_at": created_at,
    }
