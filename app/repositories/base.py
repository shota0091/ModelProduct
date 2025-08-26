from abc import ABC, abstractmethod
from typing import Optional
from app.models.profile import Profile

class ProfileRepository(ABC):
    """プロフィールの保存・取得を担うリポジトリの抽象インターフェース"""

    @abstractmethod
    def get(self, user_id: int) -> Optional[Profile]:
        """ユーザーIDで1件取得（なければ None）"""
        ...

    @abstractmethod
    def upsert(self, profile: Profile) -> None:
        """新規/更新を問わず保存"""
        ...

    @abstractmethod
    def delete(self, user_id: int) -> None:
        """削除（存在しなくてもOK）"""
        ...

    # UI向け補助（最終表示メッセージIDの保持）
    def get_message_id(self, user_id: int) -> Optional[int]:
        return None

    def set_message_id(self, user_id: int, message_id: int) -> None:
        pass
