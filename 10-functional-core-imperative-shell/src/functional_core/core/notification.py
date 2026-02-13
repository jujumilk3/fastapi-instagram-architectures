def create_notification_data(
    notification_type: str,
    actor_id: int,
    target_user_id: int,
    reference_id: int | None = None,
) -> dict:
    messages = {
        "like": "liked your post",
        "comment": "commented on your post",
        "follow": "started following you",
    }
    return {
        "user_id": target_user_id,
        "actor_id": actor_id,
        "type": notification_type,
        "reference_id": reference_id,
        "message": messages.get(notification_type, "interacted with you"),
    }
