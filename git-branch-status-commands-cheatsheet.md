# Git チートシート（ブランチ作成・ステータス・よく使うコマンド）

最小限で **迷わない** 用。コピペで使える手順に絞っています。

---

## 0) 初回設定（まだなら）
```bash
git config --global user.name  "Your Name"
git config --global user.email "you@example.com"
git config --global init.defaultBranch main
git config --global pull.rebase true   # 好み。履歴を綺麗にしやすい
```

---

## 1) ブランチ作成フロー（コピペ用）
```bash
# main を最新化
git switch main
git pull

# develop を作る（最初の一回だけ）
git switch -c develop
git push -u origin develop

# 機能ブランチ（例：Step1）を develop から切る
git switch -c feat/step1-model-repository develop
git push -u origin feat/step1-model-repository
```

> ブランチ名例：`feat/step2-views-ui`, `fix/profile-update`, `chore/ci` など

---

## 2) ステータス確認（よく使う順）
```bash
git status                      # 作業ツリー・ステージ状況
git branch --show-current       # 今いるブランチ名
git branch -vv                  # ブランチ一覧 + 追跡先 + 先行/遅延
git log --oneline --graph --decorate --all  # 履歴を図で俯瞰
git remote -v                   # リモート先確認（origin など）
```

---

## 3) よく使う日常コマンド
```bash
# 変更を見る
git diff                        # 未ステージの差分
git diff --staged               # ステージ済みの差分

# 追加・コミット
git add <path>                  # 例: git add app/models/profile.py
git add .
git commit -m "feat: add Profile model"

# Push（最初だけ -u）
git push -u origin <branch>
git push

# 最新を取り込む（安全）
git pull --rebase               # 競合が出たら直して --continue
git fetch
git rebase origin/develop       # or: git merge origin/develop
```

**コミットメッセージの例（Conventional Commits）**
```
feat: add in-memory profile repository
fix: update embed when message id missing
docs: add README for setup
refactor: split main into modules
chore: update gitignore
```

---

## 4) 競合解消の基本
```bash
# 例: develop の変更を取り込みたい
git switch feat/step1-model-repository
git fetch
git rebase origin/develop       # 競合が出たら…

# 競合したファイルの <<<< HEAD ~ >>>>> を手で修正
git add <conflicted-files>
git rebase --continue           # or: git merge --continue
```

---

## 5) 取り消し・復旧（慎重に）
```bash
git restore --staged <file>     # 間違って add した
git restore <file>              # 作業ツリーの変更を捨てる

git commit --amend              # 直前のコミットメッセージや内容を修正（未pushの時）
git reset --soft HEAD~1         # 直前のコミットを取り消し、変更は残す（未push）

git revert <commit>             # 公開済み履歴を「打ち消す」コミットを作る
git reflog                      # 迷子になったら過去のHEADを探す最終手段
```

---

## 6) PR とリリース（このプロジェクト想定）
1. `feat/*` → `develop` に PR（**Squash merge 推奨**）  
2. リリース時に `develop` → `main` に PR  
3. 任意でタグ付け：
   ```bash
   git tag -a v0.1.0 -m "Step1 release"
   git push origin v0.1.0
   ```

---

### 補足 Tips
- 新しいブランチを作るときは **常に最新の `develop` から**  
- `rebase` が苦手ならまずは `merge` でもOK（履歴が増えるだけで壊れない）  
- 大きな変更は **小さく何回かのコミット** に分けるとレビューも復旧も楽