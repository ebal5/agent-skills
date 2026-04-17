# customizations/

upstream を追跡するスキルのカスタマイズ履歴を管理するディレクトリ。

## 目的

upstream-sync PR をマージするたびに「何を取り込み、何を残し、何を変えたか」を記録する。
記録は 2 層構造で管理する。

## 2 層構造

| 層 | 場所 | 特徴 |
| --- | --- | --- |
| PR body `## Customization notes` | merge commit message に永続 | `git log` で検索可能 |
| `customizations/<skill>/NOTES.md` | このディレクトリ以下 | 時系列で閲覧しやすい |

どちらか一方では不十分なため、upstream-sync PR をマージする際は **両方** を更新する。

## 更新タイミング

upstream-sync PR をマージするとき:

1. PR body の `## Customization notes` セクションに意図を書く（merge commit message に入る）
2. `customizations/<skill>/NOTES.md` に新しいエントリを **先頭に** 追記する

## ディレクトリ規約

```text
customizations/
  <skill-name>/
    NOTES.md
```

`<skill-name>` は `skills/<skill>/SKILL.md` のフロントマター `name` フィールドと一致させる。

## NOTES.md テンプレート

新しいスキルを upstream 追跡対象に追加するときは、以下をコピーして作成する。

```markdown
# <skill> customization notes

- Upstream: `<owner/repo>` (path: `<upstream-path>`)
- 各 upstream-sync PR の merge ごとに、最新が上になるよう追記する

## Entries

### YYYY-MM-DD — upstream <short-sha> (PR #NN)

- 採用: upstream の何を取り込んだか
- 維持: こっちで残したカスタマイズと理由
- 追加/変更: 独自変更と理由
```
