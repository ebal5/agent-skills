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
