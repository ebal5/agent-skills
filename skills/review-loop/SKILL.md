---
name: review-loop
description: |
  複数視点の fresh-context reviewer を並列起動し、スコア 0-10 で triage、
  スコア閾値に応じて「対応」または「Issue 起票」を行い、新規 5+ 指摘が
  出なくなるまでループする批判的レビュープロセス。

  以下の依頼時に使用:
  - 「レビューして」「レビューラウンド」「チームレビュー」
  - 「5 以上がなくなるまで」「収束するまでレビュー」
  - 「外部視点で批判的に評価して」「独立したレビュアーで」
  - 機能実装完了後の最終品質検証

  以下では使用しない:
  - 単純な bugfix 後の軽い確認 → 通常の /simplify で十分
  - 実装前の設計議論 → /grill-me が適切
allowed-tools: Agent, Bash(gh issue:*), Bash(gh label list:*), Bash(gh pr list:*), Bash(gh pr view:*), Bash(git log:*), Bash(git diff:*), Bash(git status:*), Bash(git branch:*), TaskCreate, TaskUpdate, TaskList, TaskGet, Read, Write, Edit, Glob, Grep
model: sonnet
license: MIT
metadata:
  origin: "https://github.com/ebal5/agent-skills"
---

# Review Loop

複数視点の fresh-context reviewer を並列起動し、スコア閾値で triage、
新規 5+ 指摘が出なくなるまで収束させるレビュープロセス。

## 前提

- git ブランチでの作業 (main と比較して diff が取れる)
- GitHub リポジトリ (Issue 起票先、`gh` CLI が使える)
- 最低限のテスト・lint がパスしている状態
- `.claude/settings.json` の allow に `gh issue create:*` が入っている

## プロセス

### Phase 0: 前提確認

1. 現在のブランチ、`git log --oneline main..HEAD | head -20`、テスト状態を把握
2. 既存 open Issue を一覧 (`gh issue list --state open --limit 60 --json number,title`)
3. ユーザーに方針確認 (閾値、視点の絞り込み、最大ラウンド数など)

### Phase 1: 並列レビュー

**4 視点を並列起動** (独立した Agent として、**既存コードを追認させない**):

| 視点 | 焦点 | モデル |
| --- | --- | --- |
| **A: Correctness** | バグ、エッジケース、未検証の仮定、race、leak | Sonnet |
| **B: Agent DX** | MCP/CLI エージェントが初見で誤用する箇所、schema の機械可読性 | Sonnet |
| **C: Test Quality** | t-wada スタイル、vacuous pass、brittle、実装ミラー、実質網羅性 | Sonnet |
| **D: Architecture** | god class、責務漏れ、結合度、拡張性、層越え | **Opus** |

モデル指定は `Agent({subagent_type: "general-purpose", model: "sonnet" | "opus", ...})`
で明示する。Architecture 視点 (D) だけ Opus を残す根拠は、層越えや結合度の
判断が 1 段抽象的で、Sonnet では見落としやすいため。コスト削減効果は 4 視点
ラウンドで Opus 4→1 (75% 削減)。

各 reviewer の詳細プロンプト（焦点・出力フォーマット・スコア基準・制約）は
`prompts/<name>.md` に分離。orchestrator はファイルを読み込み、
`{{diff_or_files}}` と `{{known_issues}}` の placeholder をコンテキストに
差し替えて `Agent` に渡す。

各 Reviewer へのプロンプトに**必ず含める**:

- **既知 Issue のタイトル一覧** (重複排除)
- **スコア基準** (10=クラッシュ、8-9=確実発火、6-7=改善余地大、5=小実害、<5=省略)
- 「既存を追認しない」指示 ("動いている" "Issue 化済み" は理由にならない)
- **出力フォーマット** (場所/スコア/問題/推奨/既存 Issue 独立性)
- **最大指摘数 5-7 件で抑制** (本当に重要な順)

### Phase 2: トリアージ

Reviewer 報告を集約し、スコアで振り分け:

| スコア | 対応 |
| --- | --- |
| **≥8** | 即 FIX (コード修正 + TDD) |
| **5-7** | Issue 起票 OR FIX (ユーザー判断 / デフォルトは Issue) |
| **< 5** | 無視 |

### Phase 3: 対応実行

- **FIX**: サブエージェントに delegate、TDD 必須 (Red → Green → Refactor 各 commit)
  - Red / Green / Refactor の **実施** は Sonnet delegate
  - **Refactor プランの評価**(実施前の設計レビュー) は Opus で別 Agent に回す
    — 計画の盲点・副作用検知で Opus の抽象思考が効く。プラン自体の作成は
    Sonnet で十分
- **Issue 起票**: `gh issue create --label enhancement --body-file <body>` で一括
  - Issue body は「背景 / 再現 / 推奨修正 / スコア / 関連 Issue」構成
  - 事前に `.tmp-issues/*.md` に本文生成しておくと retry 容易

### Phase 4: 収束判定

修正/起票完了後、再び Phase 1 (別の fresh-context Agent で) を実行。

- **新規 5+ 指摘 0 件 → 収束、終了**
- **新規 5+ 指摘あり → Phase 1 に戻る**
  (既知 Issue を Reviewer に伝えて重複排除)
- Reviewer 自身に「収束判定」を求めるのも有効 (diminishing returns を検知させる)

## ループ上限

無限ループ防止のため:

- **Max 8-10 ラウンド**で打ち切り、残項目は全て Issue 起票して終了
- **Round N fix が Round N+1 で regression 指摘される連鎖**に入ったら、
  fix 前の設計を再検討
- ユーザーに中間報告 (各ラウンド完了時に進捗と次の方針)

## レビュー中のスクリプト実行

reviewer または fix エージェントが動作確認のため一時スクリプトを書いて
実行したいケース (MCP の wrap 挙動検証、SQL 生成確認、schema 比較など)。
**実行前に必ず `execute-script-safely` sub-skill で事前レビューを通す**。

詳細は同じリポジトリの execute-script-safely skill (skills/execute-script-safely/SKILL.md) を参照。要点:

- haiku Agent で 7 項目チェック (process spawn / FS write / secret read /
  network / env exfil / dynamic exec / obfuscation)
- `clean` 判定のみ実行許可、`suspicious` / `dangerous` はユーザー確認

## 新規スキル scaffold 直後の self-apply 推奨

新規に書いた skill (SKILL.md + 補助スクリプト + references) は、scaffold 直後
に本 skill を self-apply すると効果が高い。経験上:

- **round 1 (3 視点並列)**: path 参照・命名・責務分離・ライブラリ/CLI 未分離
  など、設計書段階では気づかない構造欠陥が Architecture Opus 視点で次々出る
- **round 2 (軽量、Architecture 単視点)**: round 1 の再整理で生じた二次問題
  （削除した情報が別セクションに逆流、依存の方向が逆転等）を拾う

scaffold した skill を merge する前に round 2 まで回すのがちょうどよい。
round 1 だけだと「構造を分けたが境界が曖昧」という状態で止まりがち。

### 発火パターン

- skill-creator で scaffold 直後
- dev-workflow の Phase 4 (Wrap-up) 前の最終検証として
- 「この skill レビューしてほしい」という明示的依頼

### 注意点

- reviewer には過去ラウンドの findings を渡さない（追認を避ける）
- ≥ 8 のみ即 FIX、5-7 は Issue 起票でトラッキング、という default 閾値が
  scaffold レビューでは機能しやすい（最初から高スコア指摘が大量に出るため）

## アンチパターン

- **Reviewer に前ラウンドの findings を渡してしまう** → 追認が起きて独立性喪失
- **スコア基準を甘くする** → 低スコアがノイズ化、重要事項が埋もれる
- **Issue 起票せず Fix だけで進める** → 残タスクの追跡困難、後続セッションに引き継げない
- **Reviewer を 1 視点しか起動しない** → 偏った指摘、複数視点で補完が必要
- **FIX を Refactor 省略で済ませる** → Green の妥協が次ラウンドで批判される連鎖の原因
- **無制限ループ** → 8 ラウンド超えたら diminishing returns の合図

## プロジェクト固有メモの拡張

プロジェクトごとの conventions (特定 SDK の罠、命名規則、test infrastructure
の癖など) はこの SKILL.md 末尾ではなく、プロジェクトの `CLAUDE.md` に記載
するのが望ましい。スキル起動時に `CLAUDE.md` を読んでプロジェクト固有の
配慮事項を踏まえる。
