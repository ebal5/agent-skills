# agent-skills

Personal collection of [Agent Skills](https://agentskills.io/) for AI coding agents (Claude Code, Cursor, Copilot, etc.).

## Usage

Install a single skill:

```bash
gh skill install ebal5/agent-skills <skill-name> --agent claude-code --scope user --pin v0.3.0
```

Bulk install a profile (curated lists in `install-sets/<profile>.txt`):

```bash
./install.sh common --scope user --pin v0.3.0
```

## Repository structure

Skills currently live flat under `skills/<skill-name>/SKILL.md`.
Subdirectory categorization (`skills/<category>/<skill-name>/SKILL.md`)
is also supported — `gh skill install` walks the repo tree to locate
`SKILL.md`, so both flat names and repo-relative paths can appear in
profile files.

## Scope: chezmoi dotfiles との境界

スキルを chezmoi 管理の dotfiles と別リポジトリにしているのは、主に
**配布モデル**と **project-local scope** の 2 点が理由。

- **配布・バージョニング**: スキルは `gh skill install --scope user --pin
  vX.Y.Z` でコピー配布し、バージョンを pin する。さらに
  `scripts/check_upstreams.py` による upstream 追跡と `[upstream-sync]` PR
  自動化が乗っている。chezmoi はマシン単位で `apply` する「現在状態の継続適用」
  モデルなので、pin / 移植元追跡とは噛み合わない。
- **project-local に置きたいスキルがある**: 一部のスキルはプロジェクトの
  `.claude/skills/` 配下に置きたい（`--scope project`）。chezmoi は home
  配下のテンプレート展開が前提で、プロジェクトローカル配置には向かない。

逆に言うと、**グローバル展開しかしないスキルだけ**なら dotfiles に同居させても
実害はなかった（dotfiles も個人管理なので「個人用か共有か」自体は分離理由には
ならない）。分離が効いてくるのは上記 2 点が関わるときだけ、という温度感。

スキル本文は chezmoi を前提にしない。dotfiles 側の規約に触れる場合も
「配布手段の一例」として書き、chezmoi がなくても成立する記述に留める
（例: `uv-script` のファイル配置節）。所有・配布の責務は分離しておく。

## Skill metadata conventions

Every `SKILL.md` has YAML frontmatter. The `metadata` block follows
one of two shapes depending on origin:

### Ported from another repo (tracked upstream)

```yaml
metadata:
  origin: "https://github.com/ebal5/agent-skills"
  upstream: "owner/repo"
  upstream-path: "path/inside/upstream"
  upstream-ref: "main"
  upstream-sha: <40-char SHA at last sync>
```

`scripts/check_upstreams.py` polls these skills and opens
`[upstream-sync]` PRs when `upstream-sha` falls behind `upstream-ref`.
These skills should also have an entry under `customizations/<skill>/`
(see `customizations/README.md`).

### Authored originally in this repo

```yaml
metadata:
  origin: "https://github.com/ebal5/agent-skills"
```

The `upstream-*` fields are **absent** (not empty strings).
`check_upstreams.py` skips skills without `upstream` / `upstream-ref`,
so the absence is the signal that no sync is needed. These skills
also do **not** require a `customizations/<skill>/` entry.

Do not mix the two shapes (e.g. `upstream: ""` placeholders) — the
check script's contract is "field absent → original, no sync".

## Security scanning

`.github/workflows/skill-scan.yml` runs [NVIDIA SkillSpector][skillspector]
over every `skills/<name>/` on PRs and on `main`. It runs with `--no-llm`,
so the scan is deterministic and needs no API key; `risk_score > 50` exits
non-zero and fails the job.

Everything fetched from outside is pinned by **commit SHA, not tag** —
tags are mutable, so pinning a verification tool to one defeats the point.
This applies to the scanner and to the GitHub Actions themselves.

False positives are suppressed per skill in
`.skillspector/baselines/<skill>.yaml`. Suppressions are bound to a content
hash, so a finding reactivates if the source it matched changes. Each entry
carries the reason it was accepted.

For the judgement layer on top of the scanner — evaluating intent,
separating false positives, deciding suppress-vs-fix — use the
`skill-audit` skill locally. It drives the same pinned scanner and can
enable the semantic pass via `SKILLSPECTOR_PROVIDER=claude_cli`, which
uses the local Claude CLI session instead of an API key. Run it when
reviewing an `[upstream-sync]` PR or before adopting any external skill.

[skillspector]: https://github.com/NVIDIA/skillspector

## Development (symlink workflow)

For heavy iteration on a skill while using it in a consumer project,
`gh skill install` has no built-in dev/link mode (files are copied),
so use a manual symlink:

1. Clone this repo locally
2. In the consumer project, replace the installed skill with a symlink:

   ```bash
   rm -rf .claude/skills/<skill-name>     # or ~/.claude/skills/<skill-name>
   ln -s /absolute/path/to/agent-skills/skills/<skill-name> \
         .claude/skills/<skill-name>
   ```

3. Edit in the agent-skills checkout — changes take effect immediately
4. Commit + PR from agent-skills
5. When done, remove the symlink and `gh skill install` the released version

## License

MIT
