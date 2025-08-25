# Discord Bot 起動チートシート（Step0）

## 用語ざっくり
- **Client (`discord.Client`)**  
  Bot本体。Discordにログインしてイベント（on_ready など）を受け取る窓口。

- **Intents (`discord.Intents`)**  
  Botが受け取れる情報の種類（権限フィルタ）。`default()`で最低限だけ許可。

- **CommandTree (`app_commands.CommandTree`)**  
  スラッシュコマンド（/xxx）を登録・管理する仕組み。  
  例：`tree.command(...)` で `/hello` を定義。

- **`tree.sync()`**  
  コードで定義したスラッシュコマンドをDiscord側に“反映”する操作。  
  これをやらないと新しい/変更したコマンドは使えない。

- **`.env` & `Config`**  
  `.env` に `DISCORD_BOT_TOKEN=...` を置き、`Config` で読み取って `client.run(token)` に渡す。

## 最小コード（コメント付き）
```python
# app/main.py
import discord
from discord import app_commands
from dotenv import load_dotenv
from app.config import Config

load_dotenv()  # .env を読み込み

class AppContext:
    def __init__(self):
        self.config = Config()                        # トークン取得
        self.intents = discord.Intents.default()      # 受け取るイベント種類
        self.client = discord.Client(intents=self.intents)  # Bot本体
        self.tree = app_commands.CommandTree(self.client)   # /コマンド管理

ctx = AppContext()

@ctx.client.event
async def on_ready():
    try:
        await ctx.tree.sync()     # /コマンドをDiscordに反映
    except Exception as e:
        print("sync error:", e)
    print(f"✅ Logged in as {ctx.client.user}")

ctx.client.run(ctx.config.token)  # Bot起動
```

## お試しの /hello（必要なら追加）
```python
# どこかで定義（on_readyの上あたり）
@ctx.tree.command(name="hello", description="挨拶するだけのテストコマンド")
async def hello_cmd(interaction: discord.Interaction):
    await interaction.response.send_message("やっほー！", ephemeral=True)
```
> 追加したら再起動 → `on_ready` で `sync()` が走って `/hello` が使えるようになる。

## 実行とコツ
- 実行は**プロジェクトルート**で：
  ```bash
  python -m app.main
  ```
- `.gitignore` に `.env` と `venv/` を必ず入れる（漏洩防止）。
- コマンドが出ない時は：
  - Botに必要な**権限**・**サーバー追加**済みか  
  - **`on_ready` が呼ばれているか**（ログ確認）  
  - **`sync()` がエラーなく完了しているか** を確認
```

