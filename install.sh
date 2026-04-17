#!/usr/bin/env bash
# Bulk installer for agent-skills profiles.
#
# Usage: ./install.sh <profile> [--scope user|project] [--pin <ref>]
#
# Each non-blank, non-comment line in install-sets/<profile>.txt is
# passed as the skill name to `gh skill install`. Both flat names
# ("dev-workflow") and repo-relative paths ("category/skill-name")
# work because gh skill walks the source repo to locate SKILL.md.

set -euo pipefail

scope="user"
pin=""
profile=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --scope)
      scope="$2"
      shift 2
      ;;
    --pin)
      pin="$2"
      shift 2
      ;;
    -*)
      echo "unknown option: $1" >&2
      exit 1
      ;;
    *)
      profile="$1"
      shift
      ;;
  esac
done

[[ -n "$profile" ]] || {
  echo "usage: $0 <profile> [--scope user|project] [--pin <ref>]" >&2
  exit 1
}

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
profile_file="${script_dir}/install-sets/${profile}.txt"
[[ -f "$profile_file" ]] || {
  echo "profile not found: $profile_file" >&2
  exit 1
}

while IFS= read -r line; do
  [[ -z "$line" || "$line" =~ ^[[:space:]]*# ]] && continue
  skill="${line%% *}"
  args=("ebal5/agent-skills" "$skill" "--agent" "claude-code" "--scope" "$scope")
  [[ -n "$pin" ]] && args+=("--pin" "$pin")
  echo ">> gh skill install ${args[*]}"
  gh skill install "${args[@]}"
done <"$profile_file"
