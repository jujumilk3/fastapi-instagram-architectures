from functional_core.core.types import Result


def validate_registration(
    username: str,
    email: str,
    existing_emails: list[str],
    existing_usernames: list[str],
) -> Result:
    if not username or len(username) < 3:
        return Result(success=False, error="Username must be at least 3 characters")
    if email in existing_emails:
        return Result(success=False, error="Email already registered")
    if username in existing_usernames:
        return Result(success=False, error="Username already taken")
    return Result(success=True)


def create_token_payload(user_id: int) -> dict:
    return {"sub": str(user_id)}


def validate_credentials(hashed_password: str | None, password_matches: bool) -> Result:
    if not hashed_password or not password_matches:
        return Result(success=False, error="Invalid credentials")
    return Result(success=True)
