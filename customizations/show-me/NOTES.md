# show-me customization notes

- Upstream: `humanlayer/skills`
  (path: `plugins/show-me/skills/show-me`)
- 各 upstream-sync PR の merge ごとに、最新が上になるよう追記する

## Entries

### 2026-09-20 — upstream ca7c8088 (PR #60)

3c262914 → ca7c8088 の sync。

- upstream の変更点: upstream commit `bba9d13` ("Make show-me
  user-invocable") が `skills/show-me/SKILL.md` の frontmatter に
  `disable-model-invocation: true` を追加した（本文・description の変更は
  なし）。他は無関係スキル `visual-pr` の新設のみ。
- 当リポジトリの対応: **`disable-model-invocation: true` は不採用**。
  当リポジトリの show-me は description を日本語トリガー
  （「show me」「図で」「図解して」「可視化して」等）まで拡張し、
  自動発火（モデルによる自律的な skill 選択）を維持する設計で移植した
  （2026-09-04 エントリ参照）。`disable-model-invocation: true` を入れると
  スラッシュコマンド等の明示呼び出し専用になり、この設計意図と正面から
  矛盾するため見送る。grilling の 2026-08-13 (PR #44) エントリで
  `grill-me` の `disable-model-invocation: true` を同じ理由で不採用とした
  判断を踏襲する。
- `allowed-tools` / `model` / `effort` / `metadata` / attribution コメント /
  description の拡張 / Artifact 置き換え / ~80 char re-wrap は従来どおり
  維持。
- ATTRIBUTION.md: 更新不要（show-me は専用 ATTRIBUTION.md を持たない。
  2026-09-04 の判断を継続）。
- SkillSpector: frontmatter のみの差分（かつ不採用）のため追加の手動監査は
  実施せず、CI の静的スキャン任せとする。
- 次回 sync 時の注意: upstream に新設された `visual-pr` skill は本リポジトリ
  では未追跡。取り込むかどうかは別途判断すること。差分を見るときは
  `plugins/show-me/skills/show-me/SKILL.md` だけを見ること。

### 2026-09-04 — upstream 3c262914（初回移植）

`humanlayer/skills` の `show-me` plugin (plugin.json v1.0.1) を移植した。
upstream 側は `SKILL.md` 1 枚 + `.claude-plugin/plugin.json` のみで、
参照ファイル・スクリプトの類は持たない。

- 採用: 本文ロジックをほぼそのまま取り込んだ。「今の話題を最小の視覚表現で
  見せる」という提示規範で、手札は pseudocode / call tree / component tree /
  file tree / Mermaid / diff（4 種の使い分け例）/ 全体ブロック /
  集中 HTML 1 枚。`### guidance` 節も維持。
- 追加（当リポジトリ規約）:
  - frontmatter に `allowed-tools` / `model: sonnet` / `effort: medium` /
    `license: MIT` / `metadata` ブロックを付与。
  - 本文先頭に attribution コメント
    `<!-- Based on https://github.com/humanlayer/skills ... -->`。
  - 本文を ~80 char に re-wrap（内容変更なし）。
- 変更: **HTML の見せ方を `Bash(open ...)` から Artifact に差し替えた**。
  upstream は `Bash(open path/to/show-me-{description}.html)` の 1 行だが、
  `open` は macOS 専用で、Linux や Claude Code の remote / web セッションでは
  そのまま実行不能になる。当リポジトリのスキルは特定環境を前提にしない方針
  （README「スキル本文は chezmoi を前提にしない」と同じ温度感）なので、
  `Write` → `Artifact(file_path: ...)` に置き換え、`<title>` / `favicon` /
  同一パス再 publish の注意を 3 行足した。Artifact が無い環境向けに
  「保存してパスを渡す」フォールバックを 1 文だけ残してある。
  **次回 sync ではこの節が確実に conflict する。upstream 側の `open` 行に
  戻さないこと。**
  - 副次的な利点: Artifact は Mermaid をネイティブ描画するので、
    HTML 側で描画ライブラリを読み込む必要がない。
  - `allowed-tools` に `Write, Artifact` を入れたのはこのため。ツールを
    書かずに指示だけ残すと実行不能になる（grilling の `Task` と同じ穴）。
- 変更: `description` を upstream の 1 行から、当リポジトリの
  「使用する / 使用しない」形式に拡張した。日本語トリガー（「図で」「図解して」
  「可視化して」等）を明示し、`teach-me`（実装内容の段階的理解）と
  `grilling`（計画を詰める）との境界を書いた。upstream の 1 行のままだと
  日本語セッションで発火しにくく、かつ teach-me の「解説して」系トリガーと
  competing になるため。
- コードブロック: upstream の `open` 行のフェンスだけ言語指定が無かった
  （markdownlint MD040）。置き換え後は `text` を付与している。
  他のフェンスは upstream 時点で言語指定済み。
- install-sets: `common.txt` には**入れていない**。全マシン必須ではなく
  「あると便利」枠なので、単体 install で試用し定着したら追加する判断。
- SkillSpector: この移植作業を行った remote セッションでは `uvx` の実行が
  permission classifier にブロックされたため、手元スキャンは未実施。
  PR CI の `skill-scan` ワークフロー（`--no-llm`, gate は risk_score > 50）に
  委ねる。本文を読む限りツール実行を促すのは HTML を書いて publish する
  1 箇所のみで、外部通信・認証情報・破壊的操作の指示は無い。
  CI が何か拾った場合は `skill-audit` で意図を評価し、
  `.skillspector/baselines/show-me.yaml` の登録可否を判断すること。
- 次回 sync 時の注意:
  - upstream は 5 スキル入りの mono-repo で、`check_upstreams.py` は
    repo HEAD の SHA で判定する。**別スキルの commit でも sync PR が飛ぶ**
    （grilling で実績あり）。差分を見るときは
    `plugins/show-me/skills/show-me/SKILL.md` だけを見ること。
  - `plugin.json` の `version` は当リポジトリでは追跡していない。
