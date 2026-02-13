def determine_like_action(existing_like: bool) -> str:
    return "remove" if existing_like else "add"
