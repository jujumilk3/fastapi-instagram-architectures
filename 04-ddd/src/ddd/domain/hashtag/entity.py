from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from ddd.domain.shared.entity import Entity


@dataclass
class Hashtag(Entity):
    name: str = ""
