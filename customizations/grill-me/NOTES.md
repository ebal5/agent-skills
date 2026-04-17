# grill-me customization notes

- Upstream: `mattpocock/skills` (path: `grill-me`)
- 各 upstream-sync PR の merge ごとに、最新が上になるよう追記する

## Entries

### 2026-04-17 — upstream 651eab03 (PR #7)

初回 sync。この時点で既に積まれていた独自変更を記録する。

- 採用: upstream `mattpocock/skills` の `grill-me` 本文ロジックを 651eab03 時点でそのまま取り込み
- 維持（既存カスタマイズ）:
  - Frontmatter 追加: `allowed-tools: Read, Glob, Grep, Task` / `model: sonnet` /
    `effort: high` / `license: MIT` / `metadata` ブロック
    (`origin`, `upstream`, `upstream-path`, `upstream-ref`)
  - Body 先頭の attribution コメント
    `<!-- Based on https://github.com/mattpocock/skills ... -->`
  - 独自セクション `## Checkpoint evaluation`（Sonnet ループの要所で
    Opus subagent による監査をかける運用）
  - 本文を ~80 char 幅に re-wrap（内容変更なし）
- 追加/変更:
  - `metadata.upstream-sha` を 651eab03 に設定（bot commit）
  - `metadata.upstream-path` を `skills/grill-me` → `grill-me` に修正
    （mattpocock/skills はリポジトリ直下に skill を置いているため）
