from functional_core.core.types import Result


def validate_message(content: str) -> Result:
    if not content or not content.strip():
        return Result(success=False, error="Message content is required")
    return Result(success=True)
