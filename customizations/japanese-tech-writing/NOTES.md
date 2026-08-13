# japanese-tech-writing customization notes

- Upstream: k16shikano の public gist
  (<https://gist.github.com/k16shikano/fd287c3133457c4fd8f5601d34aa817d>)
- 各 upstream-sync PR の merge ごとに、最新が上になるよう追記する

## Entries

### 2026-08-14 — 初回取り込み (gist revision c7189cdc)

`~/.claude/skills/` に手動導入されていたものを、出自とライセンスを特定した
うえでリポジトリに取り込んだ。

- **出自**: k16shikano（技術書編集者）の public gist。gist は 2026-06-16 作成、
  以後も更新が続いている
- **ライセンス**: **Unlicense**。著者自身の宣言 gist
  (<https://gist.github.com/k16shikano/67625f2a7d96e3bbdfae8d571a936063>) が
  「k16shikano の public gist にはすべて Unlicense を適用する」「日本のように
  完全なパブリックドメイン化が明確でない法域では、実務上パブリックドメイン
  相当の利用を許す」と明記している。secret gist は対象外だが、この gist は
  public であることを API で確認済み。SKILL.md 本文にライセンス記述は無いため、
  根拠はこの宣言 gist 側にある
- **本文**: gist と完全一致。**re-wrap しない**。この規範自身が「一文ごとに
  改行する」を定めており、~80 char で折り返すと規範に違反するため
- 追加したのは frontmatter、attribution コメント、markdownlint 用の
  ディレクティブのみ。末尾の余分な空行は削った（MD012 対策、内容ではない）

#### markdownlint との折り合い

`<!-- markdownlint-disable-file MD013 -->` を先頭に置いた。日本語の行は
スペースが無いため MD013 の対象外になるが、L28 だけは英語・バッククォートを
含んでスペースがあり、120 字超で検出される。一文一行の規範上は折り返せない
ので、ファイル単位で無効化した。**sync のたびに再付与すること。**

#### frontmatter の判断

- `license: Unlicense` / `metadata` / `allowed-tools: Read` / `effort: high`
- **`model` は意図的に設定しない**。他スキルは `model` を持つが、これは文章を
  書いている最中に読み込まれる「規範」であり、model を固定すると、書き手が
  意図して選んだモデルを執筆の途中で降格させてしまう。規範スキルは
  セッションのモデルを継承すべきと判断した

#### 配布範囲

`install-sets/common.txt` には**入れない**。「ユーザーグローバルは薄く保つ」
方針に対し、文章執筆系は全マシンで必要になるものではない。`coupling-*` と
同じく「リポジトリには置くが common.txt には入れない」扱いとする。

#### upstream 追跡

gist は `repos/{owner}/{repo}/commits/{ref}` で追えないため、
`scripts/check_upstreams.py` に gist 対応を入れた。`upstream` を
`gist:<owner>/<id>` 形式にすると `GET /gists/{id}` の
`history[0].version`（リビジョン ID）を SHA として追跡する。gist には ref が
無いので `upstream-ref` は `latest` 固定で、値は無視される。

- 差分表示は `https://gist.github.com/<id>/revisions`（gist には compare
  ビューが無いためリビジョン一覧を指す）
- 次回 sync 時は、この revisions ページで差分を見ること

#### セキュリティスキャン

SkillSpector v2.9.4 (`--no-llm`): 0/100 LOW / SAFE。指摘なし。
ツールもスクリプトも持たない純粋な規範テキストのため妥当。
