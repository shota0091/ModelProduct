# Step1 チートシート：Model / Repository（インメモリ）

**目的**：プロフィール情報を UI から独立させ、後で DB に差し替え可能な形にする。この段階では **UI（View）/ コマンド** には触らず、**データの持ち方と保存境界**を確立する。

---

## 1) Model: `Profile`（dataclass）
```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class Profile:
    user_id: int                   # Discordの user.id（int）
    name: str = ""                # 20文字想定（UIでバリデーション）
    comment: str = ""             # 100文字想定
    region: Optional[str] = None    # 地域（未入力可）
    prefecture: Optional[str] = None# 都道府県（未入力可）
    locked: bool = False           # 完了フラグ（最終表示後にTrue）
```
**ポイント**  
- `dataclass` は **値オブジェクト**を簡潔に表現するのに最適（`__init__` 自動生成）。  
- `Optional[str]` は **未入力を None で表す**ため。UI側の「スキップ」と相性が良い。  
- `locked` は **作成完了のスイッチ**。`/edit_profile` では region/prefecture を触らない制約にも使える。  
- **Model はドメインの状態のみ**を持つ。Discord の `Message` など**外部オブジェクトは保持しない**（疎結合）。

---

## 2) Repository IF: `ProfileRepository`
```python
from abc import ABC, abstractmethod
from typing import Optional
from app.models.profile import Profile

class ProfileRepository(ABC):
    @abstractmethod
    def get(self, user_id: int) -> Optional[Profile]: ...
    @abstractmethod
    def upsert(self, profile: Profile) -> None: ...
    @abstractmethod
    def delete(self, user_id: int) -> None: ...

    # 便利メソッド（任意実装）: 掲示メッセージIDの追跡
    def get_message_id(self, user_id: int): return None
    def set_message_id(self, user_id: int, message_id: int): ...
```
**ポイント**  
- **保存戦略の抽象化**。インメモリ→DB への差し替えは **実装クラスの変更だけ**で済む。  
- 現段階は **同期メソッド**にして簡潔化。DB 化時に `async def` に切り替える方針でもOK。  
- **UI都合の補助情報（message_id）** は本体テーブルに含めても別テーブルにしても可（DB移行時）。

---

## 3) InMemory 実装
```python
from typing import Optional, Dict
from app.models.profile import Profile
from app.repositories.base import ProfileRepository

class InMemoryProfileRepository(ProfileRepository):
    def __init__(self) -> None:
        self._store: Dict[int, Profile] = {}
        self._message_ids: Dict[int, int] = {}

    def get(self, user_id: int) -> Optional[Profile]:
        return self._store.get(user_id)

    def upsert(self, profile: Profile) -> None:
        self._store[profile.user_id] = profile

    def delete(self, user_id: int) -> None:
        self._store.pop(user_id, None)
        self._message_ids.pop(user_id, None)

    def get_message_id(self, user_id: int) -> Optional[int]:
        return self._message_ids.get(user_id)

    def set_message_id(self, user_id: int, message_id: int) -> None:
        self._message_ids[user_id] = message_id
```
**ポイント**  
- すべて **O(1)** で高速。ただし **プロセス終了で消える**（永続化なし）。  
- **スレッド安全ではない**：discord.py は基本シングルスレッドイベントループなので実害は少ないが、  将来タスクの同時実行が増えるならロックや非同期対応を検討。  
- **大人数対応**は DB 化で行う（Step5）。

---

## 4) DI（依存注入）ポイント
`app/main.py` の `AppContext` でリポジトリを組み立てて保持：
```python
from app.repositories.memory_profile import InMemoryProfileRepository

class AppContext:
    def __init__(self):
        # ...
        self.repo = InMemoryProfileRepository()
```
**メリット**  
- **Controller** から `repo` を受け取る形にすれば、**ユニットテスト**時にモックを差し替え可能。  
- DB へ切替える時は `AppContext` のこの1行を差し替えるだけ。

---

## 5) 典型ユースフロー（文字だけ）
1. `/profile` で **CreateProfileModal** を開く（Step2 以降）  
2. 名前・コメント入力 → `repo.upsert(Profile(...))` で保存  
3. 地域 Select → `region=None` のまま「未選択」なら都道府県選択を **スキップ**  
4. 最終表示メッセージの **message.id を repo.set_message_id** で保持  
5. 完了時 `locked=True`  
6. `/edit_profile` では `name/comment` のみ更新、**message を embed で編集**

---

## 6) ミニユニットテスト（pytest想定）
```python
# tests/test_repo_memory.py
from app.repositories.memory_profile import InMemoryProfileRepository
from app.models.profile import Profile

def test_upsert_get_delete():
    repo = InMemoryProfileRepository()
    p = Profile(user_id=123, name="A", comment="hi")
    repo.upsert(p)

    got = repo.get(123)
    assert got and got.name == "A"

    repo.set_message_id(123, 999)
    assert repo.get_message_id(123) == 999

    repo.delete(123)
    assert repo.get(123) is None
    assert repo.get_message_id(123) is None
```
> 使うなら `pip install pytest` → `pytest -q`。

---

## 7) よくある落とし穴
- `ModuleNotFoundError: No module named 'app'`  
  → **プロジェクトルートで** `python -m app.main` を実行。`__init__.py` も必要。  
- dataclass の **可変参照**：辞書に入れたオブジェクトは参照で保持される。  `get()` して直接フィールドを書き換えたら、**repo 側にも反映**される点は意図通りか確認。  
- **永続化されない**：Bot 再起動で消えるため、本番運用は Step5（DB）へ。  
- **DiscordのオブジェクトをModelに入れない**：循環参照・序列化不可に注意。

---

## 8) DB への移行イメージ（超要約）
**テーブル案**（MySQL想定）
```sql
CREATE TABLE profiles (
  user_id BIGINT PRIMARY KEY,
  name VARCHAR(50) NOT NULL DEFAULT '',
  comment VARCHAR(200) NOT NULL DEFAULT '',
  region VARCHAR(50) NULL,
  prefecture VARCHAR(50) NULL,
  locked BOOLEAN NOT NULL DEFAULT 0,
  message_id BIGINT NULL
);
```
**方針**  
- Repository を `MySQLProfileRepository` に差し替え。  `get/upsert/delete/get_message_id/set_message_id` を実装。  
- 非同期クライアント（`aiomysql/asyncmy`）を使うなら **IFをasync化** して Controller 側を合わせる。

---

## 9) コミット例（Conventional Commits）
```
feat(step1): add Profile model and in-memory repository
refactor: inject repository into AppContext
test: add unit test for InMemoryProfileRepository
docs: add step1 cheat sheet for model/repo
```

---

## 10) 次の一手（Step2/3 への橋渡し）
- Step2: View（Embed/Modal/Select）を `app/views/` へ分離し、**UI組み立て**を担当させる。  
- Step3: Controller に **ユースケース**（作成→地域選択→都道府県選択→最終表示→編集）を集約し、  ここで **repo** と **view_builder** を呼び出す。
