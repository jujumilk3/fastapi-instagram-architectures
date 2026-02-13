from functional_core.core.types import Result


def validate_comment(content: str) -> Result:
    if not content or not content.strip():
        return Result(success=False, error="Comment content is required")
    return Result(success=True)


def can_delete_comment(comment_owner_id: int, requester_id: int) -> bool:
    return comment_owner_id == requester_id
