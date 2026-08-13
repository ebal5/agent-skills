#!/usr/bin/env python3
"""Decide the next release version from what changed between two git refs.

The unit of distribution is a skill directory (`gh skill install` copies only
that directory) and an install-set profile (`install.sh <profile>`). So the
bump is derived from those two things alone; changes to README, CI or scripts
do not reach consumers and produce no release.

    major  a name consumers pin disappears:
           skill removed or renamed, profile removed or renamed,
           entry dropped from a profile
    minor  skill added, profile added, entry added to a profile
    patch  existing skill's content changed
    none   nothing consumer-visible changed

Usage:
    next_version.py [--prev <ref>] [--head <ref>] [--format json|tag|notes]
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys

SEMVER_TAG = re.compile(r"^v(\d+)\.(\d+)\.(\d+)$")
SKILLS_DIR = "skills"
PROFILES_DIR = "install-sets"


def run(cmd: list[str]) -> str:
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"{' '.join(cmd)} failed: {result.stderr.strip()}")
    return result.stdout


def latest_tag() -> str | None:
    """Highest semver tag reachable from HEAD."""
    out = run(["git", "tag", "--list", "v*", "--merged", "HEAD"])
    versions = []
    for line in out.splitlines():
        m = SEMVER_TAG.match(line.strip())
        if m:
            versions.append((tuple(int(g) for g in m.groups()), line.strip()))
    if not versions:
        return None
    return max(versions)[1]


def skill_trees(ref: str) -> dict[str, str]:
    """Map skill name -> tree SHA at `ref`.

    Walks nested layouts too: a directory is a skill when it holds SKILL.md.
    """
    try:
        out = run(["git", "ls-tree", "-r", "--full-tree", "--name-only", ref, f"{SKILLS_DIR}/"])
    except RuntimeError:
        return {}
    dirs = set()
    for path in out.splitlines():
        if path.endswith("/SKILL.md"):
            dirs.add(path[: -len("/SKILL.md")])
    trees = {}
    for d in sorted(dirs):
        sha = run(["git", "rev-parse", f"{ref}:{d}"]).strip()
        trees[d.split("/")[-1]] = sha
    return trees


def profiles(ref: str) -> dict[str, list[str]]:
    """Map profile name -> declared skill names at `ref`."""
    try:
        out = run(["git", "ls-tree", "--full-tree", "--name-only", ref, f"{PROFILES_DIR}/"])
    except RuntimeError:
        return {}
    result = {}
    for path in out.splitlines():
        if not path.endswith(".txt"):
            continue
        body = run(["git", "show", f"{ref}:{path}"])
        entries = [
            line.strip().split()[0]
            for line in body.splitlines()
            if line.strip() and not line.strip().startswith("#")
        ]
        result[path.split("/")[-1][: -len(".txt")]] = entries
    return result


def classify(prev: str, head: str) -> dict:
    prev_skills, head_skills = skill_trees(prev), skill_trees(head)
    prev_profiles, head_profiles = profiles(prev), profiles(head)

    added = sorted(set(head_skills) - set(prev_skills))
    removed = sorted(set(prev_skills) - set(head_skills))
    changed = sorted(
        name
        for name in set(prev_skills) & set(head_skills)
        if prev_skills[name] != head_skills[name]
    )

    profiles_added = sorted(set(head_profiles) - set(prev_profiles))
    profiles_removed = sorted(set(prev_profiles) - set(head_profiles))
    entries_added, entries_removed = [], []
    for name in sorted(set(prev_profiles) & set(head_profiles)):
        before, after = set(prev_profiles[name]), set(head_profiles[name])
        entries_added += [f"{name}: {e}" for e in sorted(after - before)]
        entries_removed += [f"{name}: {e}" for e in sorted(before - after)]

    if removed or profiles_removed or entries_removed:
        bump = "major"
    elif added or profiles_added or entries_added:
        bump = "minor"
    elif changed:
        bump = "patch"
    else:
        bump = "none"

    return {
        "bump": bump,
        "added": added,
        "removed": removed,
        "changed": changed,
        "profiles_added": profiles_added,
        "profiles_removed": profiles_removed,
        "entries_added": entries_added,
        "entries_removed": entries_removed,
    }


def bumped(tag: str, bump: str) -> str:
    m = SEMVER_TAG.match(tag)
    if m is None:
        raise ValueError(f"not a semver tag: {tag}")
    major, minor, patch = (int(g) for g in m.groups())
    if bump == "major":
        return f"v{major + 1}.0.0"
    if bump == "minor":
        return f"v{major}.{minor + 1}.0"
    if bump == "patch":
        return f"v{major}.{minor}.{patch + 1}"
    raise ValueError(f"no bump for {bump}")


def notes(version: str, prev: str, result: dict) -> str:
    lines = [version, "", f"{prev} からの変更。", ""]
    sections = [
        ("Removed (breaking)", result["removed"]),
        ("Added", result["added"]),
        ("Changed", result["changed"]),
        ("Profiles added", result["profiles_added"]),
        ("Profiles removed (breaking)", result["profiles_removed"]),
        ("Profile entries added", result["entries_added"]),
        ("Profile entries removed (breaking)", result["entries_removed"]),
    ]
    for title, items in sections:
        if not items:
            continue
        lines.append(f"{title}:")
        lines += [f"- {item}" for item in items]
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prev", help="baseline ref (default: highest semver tag)")
    parser.add_argument("--head", default="HEAD")
    parser.add_argument("--format", choices=["json", "tag", "notes"], default="json")
    args = parser.parse_args()

    prev = args.prev or latest_tag()
    if prev is None:
        print("no semver tag found; refusing to guess a baseline", file=sys.stderr)
        return 2

    result = classify(prev, args.head)
    result["prev"] = prev
    result["version"] = (
        bumped(prev, result["bump"]) if result["bump"] != "none" else None
    )

    if args.format == "tag":
        print(result["version"] or "")
    elif args.format == "notes":
        if result["version"]:
            print(notes(result["version"], prev, result), end="")
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
