#!/usr/bin/env python3
"""Check upstream skill updates and open PRs to sync recorded SHA in frontmatter."""
from __future__ import annotations

import io
import json
import os
import re
import subprocess
import sys
from pathlib import Path

from ruamel.yaml import YAML

SKILLS_DIR = Path("skills")

BOT_ENV = {
    "GIT_AUTHOR_NAME": "github-actions[bot]",
    "GIT_AUTHOR_EMAIL": "41898282+github-actions[bot]@users.noreply.github.com",
    "GIT_COMMITTER_NAME": "github-actions[bot]",
    "GIT_COMMITTER_EMAIL": "41898282+github-actions[bot]@users.noreply.github.com",
}


def run(cmd: list[str], **kwargs) -> tuple[str, int]:
    result = subprocess.run(cmd, capture_output=True, text=True, **kwargs)
    return result.stdout.strip(), result.returncode


def gh_api(path: str) -> dict | None:
    out, rc = run(["gh", "api", path])
    if rc != 0:
        return None
    return json.loads(out)


def get_latest_commit(repo: str, ref: str) -> str | None:
    data = gh_api(f"repos/{repo}/commits/{ref}")
    return data.get("sha") if data else None


def open_pr_exists(branch: str) -> bool:
    out, rc = run([
        "gh", "pr", "list",
        "--head", branch,
        "--state", "open",
        "--json", "number",
    ])
    if rc != 0:
        return False
    return len(json.loads(out)) > 0


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


def create_sync_pr(
    skill_name: str,
    skill_md: Path,
    fm,
    body: str,
    yaml: YAML,
    upstream: str,
    upstream_ref: str,
    upstream_path: str,
    recorded_sha: str | None,
    latest_sha: str,
) -> None:
    branch = f"upstream-sync/{skill_name}-{latest_sha[:8]}"

    if open_pr_exists(branch):
        print(f"[skip] {skill_name}: open PR for branch {branch} already exists")
        return

    is_initial = recorded_sha is None

    review_block = (
        "## Review\n\n"
        "- [ ] upstream の差分を確認する\n"
        "- [ ] 取り込みたい変更があれば追加コミットする\n"
        "- [ ] 独自カスタマイズを維持・調整する\n"
        "- [ ] 必要なら ATTRIBUTION.md を更新する\n"
        f"- [ ] `customizations/{skill_name}/NOTES.md` にも追記する\n\n"
        "## Customization notes\n\n"
        "<!-- この PR で upstream の何を採用し、こっちで何を残した/変えたか、意図を書く。\n"
        "     merge されると PR body が main の commit message に入り、git log で検索できる。 -->\n\n"
        "---\n"
        "Merging this PR advances `metadata.upstream-sha` in SKILL.md.\n"
        "Additional commits on this branch are welcome (the bot will not rebase)."
    )

    if is_initial:
        pr_title = f"[upstream-sync] initial: {skill_name} ({upstream} @ {latest_sha[:8]})"
        pr_body = (
            f"Initial upstream sync for **{skill_name}**.\n\n"
            f"- Skill: `{skill_name}`\n"
            f"- Upstream: `{upstream}` (`{upstream_ref}`)\n"
            f"- Upstream path: `{upstream_path}`\n"
            f"- Previous SHA: `none`\n"
            f"- Latest SHA: `{latest_sha}`\n\n"
            f"{review_block}"
        )
    else:
        pr_title = f"[upstream-sync] {skill_name}: {upstream} -> {latest_sha[:8]}"
        compare_url = (
            f"https://github.com/{upstream}/compare/{recorded_sha}...{latest_sha}"
        )
        pr_body = (
            f"Upstream **{upstream}** (`{upstream_ref}`) has new commits.\n\n"
            f"- Skill: `{skill_name}`\n"
            f"- Upstream path: `{upstream_path}`\n"
            f"- Previous SHA: `{recorded_sha}`\n"
            f"- Latest SHA: `{latest_sha}`\n"
            f"- Compare: {compare_url}\n\n"
            f"{review_block}"
        )

    # Create branch, update SKILL.md, commit, push, open PR
    _, rc = run(["git", "checkout", "-b", branch])
    if rc != 0:
        print(f"WARN: failed to create branch {branch}", file=sys.stderr)
        return

    try:
        metadata = fm.get("metadata") or {}
        metadata["upstream-sha"] = latest_sha
        fm["metadata"] = metadata
        write_skill_md(skill_md, fm, body, yaml)

        run(["git", "add", str(skill_md)])
        commit_msg = f"chore(upstream-sync): record {skill_name} @ {latest_sha[:8]}"
        _, rc = run(
            ["git", "commit", "-m", commit_msg],
            env={**os.environ, **BOT_ENV},
        )
        if rc != 0:
            print(f"WARN: git commit failed for {skill_name}", file=sys.stderr)
            return

        _, rc = run(["git", "push", "origin", branch])
        if rc != 0:
            print(f"WARN: git push failed for branch {branch}", file=sys.stderr)
            return

        out, rc = run([
            "gh", "pr", "create",
            "--title", pr_title,
            "--body", pr_body,
            "--base", "main",
            "--head", branch,
        ])
        if rc == 0:
            print(f"[pr] {skill_name}: created {out}")
        else:
            print(f"WARN: failed to create PR for {skill_name}", file=sys.stderr)
    finally:
        run(["git", "checkout", "main"])


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

        if recorded_sha == latest_sha:
            print(f"[up-to-date] {skill_name}: {latest_sha[:7]}")
            continue

        upstream_path = metadata.get("upstream-path", "")
        if recorded_sha is None:
            print(f"[init] {skill_name}: creating initial sync PR @ {latest_sha[:8]}")
        else:
            print(f"[diff] {skill_name}: {recorded_sha[:7]} -> {latest_sha[:7]}")

        create_sync_pr(
            skill_name=skill_name,
            skill_md=skill_md,
            fm=fm,
            body=body,
            yaml=yaml,
            upstream=upstream,
            upstream_ref=upstream_ref,
            upstream_path=upstream_path,
            recorded_sha=recorded_sha,
            latest_sha=latest_sha,
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
