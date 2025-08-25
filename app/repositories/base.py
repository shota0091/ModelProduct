from abc import ABC, abstractmethod
from typing import Optional
from app.models.profile import Profile

class ProfileRepository(ABC):
    @abstractmethod
    def get(self, user_id: int) -> Optional[Profile]:
        ...

    @abstractmethod
    def upsert(self, profile: Profile) -> None:
        ...

    @abstractmethod
    def delete(self, user_id: int) -> None:
        ...

    # 便利メソッド（メッセージID追跡：必要な実装だけ上書き）
    def get_message_id(self, user_id: int) -> Optional[int]:
        return None

    def set_message_id(self, user_id: int, message_id: int) -> None:
        pass
