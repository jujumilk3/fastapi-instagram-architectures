from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Result:
    success: bool
    error: str = ""
    data: Any = None
