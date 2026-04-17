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

## License

MIT
