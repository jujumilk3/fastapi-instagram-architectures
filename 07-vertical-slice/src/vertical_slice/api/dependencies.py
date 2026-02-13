from __future__ import annotations

from vertical_slice.shared.mediator import mediator
from vertical_slice.shared.security import get_current_user_id


def get_mediator():
    return mediator


__all__ = ["get_current_user_id", "get_mediator"]
