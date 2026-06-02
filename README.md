# agent-skills

Personal collection of [Agent Skills](https://agentskills.io/) for AI coding agents (Claude Code, Cursor, Copilot, etc.).

## Usage

Install a single skill:

```bash
gh skill install ebal5/agent-skills <skill-name> --agent claude-code --scope user --pin v0.1.0
```

Bulk install a profile (curated lists in `install-sets/<profile>.txt`):

```bash
./install.sh common --scope user --pin v0.1.0
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

両者は参照しあう（例: `uv-script` / `dev-workflow` が chezmoi 適用を前提に
言及する）が、所有・配布の責務は分離している。

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
