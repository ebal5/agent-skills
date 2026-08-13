# cognitive-rhythm-writing customization notes

- Upstream: k16shikano の public gist
  (<https://gist.github.com/k16shikano/eb2929f13ed19c97188393d297be8432>)
- 各 upstream-sync PR の merge ごとに、最新が上になるよう追記する

## Entries

### 2026-08-14 — 初回取り込み (gist revision a3b1e26b)

`~/.claude/skills/` に手動導入されていたものを、出自とライセンスを特定した
うえでリポジトリに取り込んだ。判断の詳細は
[[japanese-tech-writing]] の NOTES と共通なので、そちらも参照。

- **出自**: k16shikano の public gist（2026-07-09 作成）。
  [[japanese-tech-writing]] の作者と同一
- **ライセンス**: **Unlicense**（著者の宣言 gist
  <https://gist.github.com/k16shikano/67625f2a7d96e3bbdfae8d571a936063>
  が public gist 全体に適用すると明記）。public であることは API で確認済み
- **本文**: gist と完全一致。re-wrap しない（併用先の
  japanese-tech-writing が「一文ごとに改行する」を定めているため）
- `model` を設定しない理由、`common.txt` に入れない理由は
  [[japanese-tech-writing]] の NOTES と同じ

#### 2 件セットで扱うこと

本文冒頭に「作業前に `../japanese-tech-writing/SKILL.md` を読む」という
**相対パス依存**がある。flat 配置（`skills/<name>/`）では隣接ディレクトリ
として解決できるが、片方だけインストールすると壊れる。

- `install-sets` に入れるなら必ず 2 件セットにする
- どちらかを削除・改名するときはもう一方の参照も直す
- SkillSpector の AS3 (skill enumeration) 判定に当たり得る参照だが、
  今回のスキャンでは検出されなかった

#### セキュリティスキャン

SkillSpector v2.9.4 (`--no-llm`): 0/100 LOW / SAFE。指摘なし。
