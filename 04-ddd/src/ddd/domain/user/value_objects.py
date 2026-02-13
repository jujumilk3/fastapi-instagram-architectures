from __future__ import annotations

import re
from dataclasses import dataclass

from ddd.domain.shared.value_object import ValueObject


@dataclass(frozen=True)
class Email(ValueObject):
    value: str

    def __post_init__(self):
        if not re.match(r"[^@]+@[^@]+\.[^@]+", self.value):
            raise ValueError(f"Invalid email: {self.value}")


@dataclass(frozen=True)
class Username(ValueObject):
    value: str

    def __post_init__(self):
        if not self.value or len(self.value) < 1 or len(self.value) > 50:
            raise ValueError(f"Username must be 1-50 characters: {self.value}")
