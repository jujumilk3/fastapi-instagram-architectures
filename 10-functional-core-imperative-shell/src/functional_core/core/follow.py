from functional_core.core.types import Result


def validate_follow(follower_id: int, following_id: int) -> Result:
    if follower_id == following_id:
        return Result(success=False, error="Cannot follow yourself")
    return Result(success=True)
