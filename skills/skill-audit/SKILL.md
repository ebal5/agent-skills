---
name: skill-audit
description: |
  Agent Skill のセキュリティ監査。NVIDIA SkillSpector で静的スキャンし、
  検出結果の意図を評価して誤検知を切り分け、baseline 登録か修正かを判断する。

  以下の依頼時に使用:
  - 「スキルを監査」「スキルをスキャン」「skill を security チェック」
  - 「このスキル入れて安全？」「インストール前に確認」
  - upstream-sync PR のレビュー時、外部スキルを取り込む前
  - 「skillspector」「skill audit」「scan skill」「audit skill」
allowed-tools: Read, Glob, Grep, Edit, Bash(uvx:*), Bash(ls:*)
model: sonnet
effort: high
license: MIT
metadata:
  origin: "https://github.com/ebal5/agent-skills"
---

# Skill Audit

Agent Skill をインストール前・取り込み前に監査する。
CI (`.github/workflows/skill-scan.yml`) は同じスキャナを `--no-llm` で
ゲートとして回している。このスキルはその上に**意図の評価**を乗せる担当で、
CI が落ちたとき・外部スキルを取り込むときに手元で使う。

## 前提

`uv` が必要（<https://docs.astral.sh/uv/getting-started/installation/>）。

スキャナは commit SHA で pin する。タグは付け替え可能なので使わない。
**SHA は `.github/workflows/skill-scan.yml` の `SKILLSPECTOR_REF` と必ず揃える。**

```text
SKILLSPECTOR = git+https://github.com/NVIDIA/skillspector.git@2d198ab910add401cad658d1087e7c7ba24fd640
```

## Step 1: 静的スキャン

まず LLM なしで走らせる。決定的で、鍵も要らない。

```bash
uvx --from "$SKILLSPECTOR" skillspector scan <skill-dir>/ --no-llm --format markdown
```

既存の baseline があれば併せて渡す。

```bash
uvx --from "$SKILLSPECTOR" skillspector scan <skill-dir>/ --no-llm \
  --baseline .skillspector/baselines/<skill>.yaml --show-suppressed
```

終了コードは `0`: risk_score ≤ 50 / `1`: > 50 (DO NOT INSTALL) / `2`: エラー。

## Step 2: semantic 解析（必要なとき）

静的解析で判断がつかない、または外部由来のスキルを初めて取り込む場合は
LLM 段も有効にする。ローカルの `claude` 認証をそのまま使うので
API キーは不要。

```bash
SKILLSPECTOR_PROVIDER=claude_cli uvx --from "$SKILLSPECTOR" \
  skillspector scan <skill-dir>/
```

## Step 3: 検出結果の triage

スキャナはパターンを機械的に拾う。**意図の評価はこちらの仕事**。
検出ごとに該当行を実際に読み、次のどれかに分類する。

- **真の問題** → 取り込まない、または該当箇所を修正する
- **誤検知** → baseline に登録する（Step 4）
- **判断保留** → ユーザーに提示して判断を仰ぐ。勝手に baseline に入れない

このリポジトリで実際に出た誤検知の型:

- **危険例のカタログ**: `execute-script-safely` のように「こういうコードを
  弾け」という negative example を本文に持つスキルは、その例文が
  PE3 (credential access) / SC2 (external script fetching) /
  TM1 (tool parameter abuse) に当たる
- **意図的な cross-skill 参照**: AS3 (skill enumeration)。このリポジトリは
  sub-skill 合成を明示的な設計としているため、他スキルへの参照は正常

「security 系スキルだから誤検知だろう」で流さないこと。
**該当行を読んで、それが記述なのか実行なのかを確認してから**分類する。

## Step 4: baseline 登録

誤検知と判断したものだけを抑制する。理由を必ず残す。

```bash
uvx --from "$SKILLSPECTOR" skillspector baseline <skill-dir>/ --no-llm \
  -o .skillspector/baselines/<skill>.yaml \
  --reason "<なぜ誤検知と判断したか。判断日も入れる>"
```

抑制は内容ハッシュに紐づくので、該当箇所が書き換わると再び検出される。
`baseline` コマンドは**現在の検出をすべて**抑制するため、真の問題が
混ざっている状態で走らせないこと。

登録後、抑制が効いていることを確認する。

```bash
uvx --from "$SKILLSPECTOR" skillspector scan <skill-dir>/ --no-llm \
  --baseline .skillspector/baselines/<skill>.yaml
```

## Step 5: 報告

- スキル名 / risk_score / severity / recommendation
- 検出ごとの分類（真の問題 / 誤検知 / 保留）と、そう判断した根拠
- baseline に足したものがあれば、その内容
- 取り込み可否の推奨

## やらないこと

- スキャナが SAFE を返したことをもって「安全」と報告しない。静的解析は
  既知パターンの検出であって、悪意の不在の証明ではない
- 判断がつかないものを黙って baseline に入れない
- pin した SHA を勝手に上げない。更新は独立した変更として扱う
