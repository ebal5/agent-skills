#!/usr/bin/env python3
"""Check upstream skill updates and sync recorded SHA in frontmatter."""
from __future__ import annotations

import io
import json
import re
import subprocess
import sys
from pathlib import Path

from ruamel.yaml import YAML

SKILLS_DIR = Path("skills")


def run(cmd: list[str]) -> tuple[str, int]:
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout.strip(), result.returncode


def gh_api(path: str) -> dict | None:
    out, rc = run(["gh", "api", path])
    if rc != 0:
        return None
    return json.loads(out)


def get_latest_commit(repo: str, ref: str) -> str | None:
    data = gh_api(f"repos/{repo}/commits/{ref}")
    return data.get("sha") if data else None


def issue_exists(title_prefix: str) -> bool:
    out, rc = run([
        "gh", "issue", "list",
        "--search", title_prefix,
        "--state", "open",
        "--json", "title",
    ])
    if rc != 0:
        return False
    return any(title_prefix in i["title"] for i in json.loads(out))


def split_frontmatter(text: str) -> tuple[str, str] | None:
    """Split SKILL.md into (frontmatter_text, body_text) using regex."""
    m = re.match(r"\A---\n(.*?)\n---\n(.*)\Z", text, re.DOTALL)
    if m is None:
        return None
    return m.group(1), m.group(2)


def load_frontmatter(fm_text: str, yaml: YAML):
    return yaml.load(fm_text)


def dump_frontmatter(fm, yaml: YAML) -> str:
    buf = io.StringIO()
    yaml.dump(fm, buf)
    return buf.getvalue()


def write_skill_md(skill_md: Path, fm, body: str, yaml: YAML) -> None:
    fm_text = dump_frontmatter(fm, yaml)
    skill_md.write_text(f"---\n{fm_text}---\n{body}")


def main() -> int:
    yaml = YAML()
    yaml.preserve_quotes = True

    for skill_dir in sorted(SKILLS_DIR.iterdir()):
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            continue
        content = skill_md.read_text()
        split = split_frontmatter(content)
        if split is None:
            continue
        fm_text, body = split
        try:
            fm = load_frontmatter(fm_text, yaml)
        except Exception as e:
            print(f"WARN: failed to parse {skill_md}: {e}", file=sys.stderr)
            continue
        if fm is None:
            continue
        metadata = fm.get("metadata") or {}
        upstream = metadata.get("upstream")
        upstream_ref = metadata.get("upstream-ref")
        if not upstream or not upstream_ref:
            continue

        skill_name = fm.get("name", skill_dir.name)
        recorded_sha = metadata.get("upstream-sha")
        latest_sha = get_latest_commit(upstream, upstream_ref)
        if latest_sha is None:
            print(
                f"WARN: could not fetch latest commit for {upstream}@{upstream_ref}",
                file=sys.stderr,
            )
            continue

        if recorded_sha is None:
            # Initial sync: record without creating an issue
            print(f"[init] {skill_name}: recording initial SHA {latest_sha[:7]}")
            metadata["upstream-sha"] = latest_sha
            fm["metadata"] = metadata
            write_skill_md(skill_md, fm, body, yaml)
            continue

        if recorded_sha == latest_sha:
            print(f"[up-to-date] {skill_name}: {latest_sha[:7]}")
            continue

        # Upstream has new commits
        title_prefix = f"[upstream-update] {skill_name}: {upstream}"
        title = f"{title_prefix} の更新あり"
        if issue_exists(title_prefix):
            print(f"[skip] {skill_name}: issue already exists")
        else:
            upstream_path = metadata.get("upstream-path", "")
            compare_url = (
                f"https://github.com/{upstream}/compare/{recorded_sha}...{latest_sha}"
            )
            body_text = (
                f"Upstream **{upstream}** (`{upstream_ref}`) has new commits.\n\n"
                f"- Skill: `{skill_name}`\n"
                f"- Upstream path: `{upstream_path}`\n"
                f"- Previous SHA: `{recorded_sha}`\n"
                f"- Latest SHA: `{latest_sha}`\n"
                f"- Compare: {compare_url}\n\n"
                "Review changes and update the skill if needed. "
                "The recorded SHA has been advanced automatically to the latest."
            )
            out, rc = run([
                "gh", "issue", "create",
                "--title", title,
                "--body", body_text,
            ])
            if rc == 0:
                print(f"[issue] {skill_name}: created {out}")
            else:
                print(
                    f"WARN: failed to create issue for {skill_name}", file=sys.stderr
                )

        # Always advance SHA to avoid repeated diffs on next run
        metadata["upstream-sha"] = latest_sha
        fm["metadata"] = metadata
        write_skill_md(skill_md, fm, body, yaml)

    return 0


if __name__ == "__main__":
    sys.exit(main())
