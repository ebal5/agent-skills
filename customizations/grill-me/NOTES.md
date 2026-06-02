# grill-me customization notes

- Upstream: `mattpocock/skills` (path: `skills/productivity/grill-me`)
- 各 upstream-sync PR の merge ごとに、最新が上になるよう追記する

## Entries

### 2026-06-02 — upstream aaf2453f (PR #32)

651eab03 → aaf2453f の sync。

- 確認: upstream の `grill-me/SKILL.md` 本文は 651eab03 と aaf2453f で完全一致。
  取り込むべき本文変更はなし。
- upstream の唯一の関連変更はリポジトリ再編で、skill の置き場所が
  `grill-me/` → `skills/productivity/grill-me/` に移動した。
- 維持（既存カスタマイズ）: frontmatter 追加分、attribution コメント、
  独自セクション `## Checkpoint evaluation`、~80 char re-wrap をすべて継続。
- 追加/変更:
  - `metadata.upstream-sha` を aaf2453f に更新（bot commit）
  - `metadata.upstream-path` を `grill-me` → `skills/productivity/grill-me`
    に修正（upstream の移動に追従。SHA 算出には未使用の情報フィールドだが
    今後の diff 確認のため正確に保つ）
- ATTRIBUTION.md: grill-me は専用 ATTRIBUTION.md を持たず、attribution は
  本文先頭のコメントと `license: MIT` / `metadata` で表現しているため更新不要。
- 補足: #26–#31 は同じ 651eab03 起点の旧 weekly sync PR。本 PR (#32) が
  最新 SHA を取り込むため、merge 後にまとめてクローズした。

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
