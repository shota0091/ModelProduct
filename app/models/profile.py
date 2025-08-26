from dataclasses import dataclass
from typing import Optional

@dataclass
class Profile:
    user_id: int
    name: str = ""
    comment: str = ""
    region: Optional[str] = None
    prefecture: Optional[str] = None
    locked: bool = False
