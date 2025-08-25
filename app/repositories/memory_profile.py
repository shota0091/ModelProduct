from typing import Optional, Dict
from app.models.profile import Profile
from app.repositories.base import ProfileRepository

class InMemoryProfileRepository(ProfileRepository):
    def __init__(self) -> None:
        self._store: Dict[int, Profile] = {}
        self._message_ids: Dict[int, int] = {}

    # --- CRUD ---
    def get(self, user_id: int) -> Optional[Profile]:
        return self._store.get(user_id)

    def upsert(self, profile: Profile) -> None:
        self._store[profile.user_id] = profile

    def delete(self, user_id: int) -> None:
        self._store.pop(user_id, None)
        self._message_ids.pop(user_id, None)

    # --- message id helpers ---
    def get_message_id(self, user_id: int) -> Optional[int]:
        return self._message_ids.get(user_id)

    def set_message_id(self, user_id: int, message_id: int) -> None:
        self._message_ids[user_id] = message_id
