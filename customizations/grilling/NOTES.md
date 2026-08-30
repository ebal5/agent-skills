# grilling customization notes

- Upstream: `mattpocock/skills` (path: `skills/productivity/grilling`。
  84fdeffd で本文が `skills/productivity/grill-me` から移動した)
- 2026-08-13 (PR #44) までは当リポジトリでも `grill-me` という名前だった。
  以前の経緯は下の古いエントリを参照
- 各 upstream-sync PR の merge ごとに、最新が上になるよう追記する

## Entries

### 2026-08-30 — upstream 6654f6b6 (PR #55)

5b15a47f → 6654f6b6 の sync。

- upstream の変更点: `skills/productivity/grilling/SKILL.md` は
  5b15a47f と 6654f6b6 で完全一致（バイト単位で同一。diff なし）。
  この区間の upstream commit はリポジトリ内の別スキル (`skills/in-progress/retro`
  の新設) のみで、`grilling` には無関係。取り込むべき本文変更はなし。
- 当リポジトリの対応: `metadata.upstream-sha` の更新のみ（bot commit）。
  本文・frontmatter のそれ以外の変更なし。
- ATTRIBUTION.md: 更新不要（PR #44 の判断を継続）。
- SkillSpector: 本文変更なしのため追加の手動監査は実施せず、CI の静的
  スキャン任せとする。
- 次回 sync 時の注意: 差分を見るときは `grilling` を見ること。

### 2026-08-23 — upstream 5b15a47f (PR #54)

068b6e0c → 5b15a47f の sync。

- upstream の変更点 (upstream PR #917 "Separate questions in a round with an
  HR"): フォーマット例を 1 問だけのものから、`---` で区切った 2 問構成の
  ラウンド全体を示す例に拡張。あわせて見出し文言も
  "Each question should be formatted like so:" →
  "Format a round like so:" に変更。ロジック・frontmatter の変更はなし。
- 当リポジトリの対応: 同じ変更をローカルの再ラップ済み本文にも適用した
  （見出し文言の変更、および Q1 の後に `---` 区切りと Q2 の例を追加）。
  本文冒頭で「フロンティア全体を 1 ラウンドでまとめて聞く」ことは既に
  明記済みのため、意味的な矛盾はない。
- `allowed-tools` / `model` / `effort` / `metadata` / attribution コメント /
  ~80 char re-wrap は従来どおり維持。
- ATTRIBUTION.md: 更新不要（PR #44 の判断を継続）。
- SkillSpector: 例のフォーマットのみの変更でツール権限や挙動に変化はない
  ため、CI の静的スキャン任せとし追加の手動監査は実施せず。
- 次回 sync 時の注意: 差分を見るときは `grilling` を見ること。

### 2026-08-18 — upstream 068b6e0c (PR #53)

84fdeffd → 068b6e0c の sync。

- upstream の変更点: 本文中の em dash (`—`) をコロン / セミコロンに置き換える
  句読点クリーンアップのみ（"standardizes skill-invocation punctuation for
  clearer plain-text/AI reading" 系のリポジトリ横断コミットの一部）。
  frontmatter・ロジックの変更はなし。
- 当リポジトリの対応: 同じ置き換えをローカルの再ラップ済み本文にも適用した
  （4 箇所: "settled — the questions" → "settled: the questions"、
  "reshapes the tree — settled" → "reshapes the tree: settled"、
  "worth it — don't ask" → "worth it; don't ask"、
  "wait for the result — ask" → "wait for the result; ask"、
  "user's — put each" → "user's: put each"）。
  独自に緩めた「事実調査は自分で / 範囲が広いときは sub-agent」の文面は
  upstream 側でも変更されていないため維持。
- `allowed-tools` / `model` / `effort` / `metadata` / attribution コメント /
  ~80 char re-wrap は従来どおり維持。
- ATTRIBUTION.md: 更新不要（PR #44 の判断を継続）。
- SkillSpector: CI の `skillspector` チェックが green（句読点のみの変更で
  ツール権限や挙動に変化なしのため、追加の手動監査は実施せず）。
- 次回 sync 時の注意: 差分を見るときは `grilling` を見ること。

### 2026-08-13 — upstream 84fdeffd (PR #44) / `grill-me` → `grilling` に改名

be55a797 → 84fdeffd の sync。**upstream が grill-me を分割した**ため、
本文をまるごと差し替え、併せてスキル名も upstream 側の実体に合わせた。

- upstream の再編: `skills/productivity/grill-me/SKILL.md` は
  `description: A relentless interview to sharpen a plan or design.` /
  `disable-model-invocation: true` と本文 1 行 ``Run a `/grilling` session.``
  だけのランチャーに縮小され、実体が新スキル
  `skills/productivity/grilling/SKILL.md` に移った。同時に本文も大幅改稿。
- 当リポジトリの対応: **`grilling` だけを取り込み、ランチャーは持たない**。
  upstream の `grill-me` は `/grill-me` という別名を用意するためだけの
  スタブで、`grilling` の description が "grill" 系トリガーを含むため、
  ランチャーが無くても自動発火・`/grilling` 起動とも成立する。
  1 スキル単位で配布する当リポジトリで 2 本に分ける利点がない。
  `disable-model-invocation: true` も不採用 (自動発火を残したい)。
- 改名の実務: `skills/grill-me/` → `skills/grilling/`、
  `customizations/grill-me/` → `customizations/grilling/`、
  `install-sets/common.txt` のエントリ、`markdown-check` / `teach-me` /
  `review-loop` 本文中の言及も更新した。**インストール済みマシンでは
  古い `grill-me` が残るので手で消すこと**。
- `description` は upstream `grilling` の内容に寄せつつ、"grill me" という
  トリガー語を明示して従来の呼び出し方を維持した。
- 取り込んだ本文の変更点 (upstream `grilling` 由来):
  - 「1 問ずつ聞く」→ **rounds / frontier 方式**。前提が解決済みの質問を
    frontier としてまとめて 1 ラウンドで出し、回答を待ってから再計算する。
  - 質問の書式を明示 (`❓ **Q1** - **<title>**: ...` と `➡️ <推奨案>`)。
  - 事実調査は「ユーザーに聞かずエージェント側が取りに行く」、調査中の
    ブロックを避け downstream の質問だけ待たせる、という指示を追加。
  - 終了条件が「frontier が空」に明文化され、ユーザーの合意確認までは
    実装に着手しないことが明示された。
- ローカルで調整した点:
  - 事実調査の一文: upstream は無条件に「sub-agent を dispatch しろ」だが、
    数回のツール呼び出しで済む調査まで委譲するのは
    グローバル CLAUDE.md の委譲方針に反するため、
    「自分で調べる / 範囲が広いときは sub-agent」に緩めた。
  - `allowed-tools` に `Agent` を追加。sub-agent の記述を残す以上、
    ツールが無いと指示が実行不能になる (2026-08-13 の `Task` と同じ穴)。
    なお 2026-08-13 に外したのは「自分の作業を検証させる subagent」であり、
    ここでの事実調査の委譲は Opus 5 の指針とは衝突しない。
  - コードブロックに言語指定 `text` を付与 (markdownlint MD040 対策)。
  - 本文を ~80 char に re-wrap。attribution コメント、`license: MIT` /
    `metadata` ブロック、`model: sonnet` / `effort: high` は従来どおり維持。
- `metadata.upstream-path` を `skills/productivity/grill-me` →
  `skills/productivity/grilling` に変更。本文の出所を指す情報フィールドで、
  `check_upstreams.py` は repo HEAD の SHA しか見ないため sync 動作には影響しない。
- セキュリティスキャン (SkillSpector v2.9.4, `--no-llm`): **8/100 LOW / SAFE**。
  MEDIUM の EA2 (Autonomous Decision Making) が 1 件、「事実は自分で調べる」の
  行に出たが誤検知と判断した。決定は必ずユーザーに戻す設計
  (`The _decisions_ are the user's` / `Do not act on it until the user confirms`)
  で、ツールも読み取り系に限られている。ゲート (>50) は通るため baseline には
  登録せず、シグナルとして残す。
- 次回 sync 時の注意: 差分を見るときは `grill-me` ではなく **`grilling`**
  を見ること。upstream の `grill-me` はランチャーのままのはず。

### 2026-08-13 — upstream be55a797 (PR #35)

aaf2453f → be55a797 の sync。事後記録 (当時 NOTES への追記が漏れていた)。

- 確認: upstream の `skills/productivity/grill-me/SKILL.md` は aaf2453f と
  be55a797 で**完全一致**。取り込むべき本文変更はなし。
- 変更は `metadata.upstream-sha` の更新 (bot commit) のみ。

### 2026-08-13 — ローカル変更のみ（upstream sync ではない）

独自セクション `## Checkpoint evaluation` を **削除**した。upstream との
差分を減らす方向の変更で、`upstream-sha` は aaf2453f のまま据え置き。

- 削除理由: Claude Opus 5 のプロンプティング指針
  (<https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5>)
  が「サブエージェントを自分の作業の検証・二重チェックに使わない」
  「明示的な検証指示は over-verification を招く」としており抵触するため。
  加えて本文が指定していた `Task` ツールは現行ハーネスに存在せず
  (`Agent` が該当)、指示自体が実行不能だった。
- 併せて frontmatter の `allowed-tools` から `Task` を除去し
  `Read, Glob, Grep` に縮小。
- 維持: attribution コメント、`license: MIT` / `metadata` ブロック、
  ~80 char re-wrap。
- 次回 sync 時の注意: 本セクションは upstream 由来ではないため、
  upstream 側に対応する記述は存在しない。復活させないこと。

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
