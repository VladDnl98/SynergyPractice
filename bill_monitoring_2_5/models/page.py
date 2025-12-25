from dataclasses import dataclass
from typing import Optional

@dataclass
class Page:
    url: str
    name: str
    slow_threshold: float

    status_code: Optional[int] = None
    success: bool = False
    error: Optional[str] = None
    response_time: Optional[float] = None
    was_slow: bool = False
    was_failed: bool = False