#!/usr/bin/env bash
set -euo pipefail

ROOT="${BITPOD_APP_ROOT:-/Users/cjarguello/BitPod-App}"
REGISTRY_FILE="${BITPOD_REPO_REGISTRY_FILE:-$ROOT/bitpod-tools/config/repo_registry.tsv}"
TMP_FILE="$(mktemp "${TMPDIR:-/tmp}/repo_registry.XXXXXX")"
trap 'rm -f "$TMP_FILE"' EXIT

echo "# repo|relative_path|pulse_enabled|cleanup_enabled|thread_visible|verified|notes" > "$TMP_FILE"

find "$ROOT" -maxdepth 1 -mindepth 1 -type d | sort | while IFS= read -r path; do
  local_name="$(basename "$path")"
  has_git=0
  has_github=0
  [[ -d "$path/.git" ]] && has_git=1
  [[ -d "$path/.github" ]] && has_github=1
  [[ "$has_git" -eq 1 || "$has_github" -eq 1 ]] || continue

  existing_row="$(awk -F'|' -v repo="$local_name" '$1 == repo {print $0; exit}' "$REGISTRY_FILE" 2>/dev/null || true)"
  if [[ -n "$existing_row" ]]; then
    echo "$existing_row" >> "$TMP_FILE"
    continue
  fi

  if [[ "$has_git" -eq 1 ]]; then
    echo "$local_name|$local_name|1|1|1|1|auto-discovered via .git" >> "$TMP_FILE"
  else
    echo "$local_name|$local_name|0|0|0|0|candidate discovered via .github only; verify manually before enabling" >> "$TMP_FILE"
  fi
done

mv "$TMP_FILE" "$REGISTRY_FILE"
echo "Refreshed repo registry at $REGISTRY_FILE"
