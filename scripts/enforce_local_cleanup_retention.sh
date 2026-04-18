#!/usr/bin/env bash
set -euo pipefail

SCRIPT_REF="${BASH_SOURCE[0]:-$0}"
SCRIPT_DIR="$(cd -- "$(dirname "$SCRIPT_REF")" && pwd)"
ROOT_DEFAULT="$(cd -- "$SCRIPT_DIR/../.." && pwd)"
ROOT="${BITPOD_APP_ROOT:-${WORKSPACE:-$ROOT_DEFAULT}}"
CONTRACT_FILE="${BITPOD_LOCAL_WORKSPACE_CONTRACT_FILE:-$ROOT/bitpod-docs/process/local-workspace-skeleton-contract.toml}"
PROFILE="${BITPOD_LOCAL_WORKSPACE_PROFILE:-personal_machine_full}"

PROHIBITED_DAYS="${BITPOD_PROHIBITED_PATH_RETENTION_DAYS:-30}"
TRASH_TO_PURGE_DAYS="${BITPOD_LOCAL_TRASH_PURGE_DAYS:-30}"
PURGE_TO_OS_TRASH_DAYS="${BITPOD_LOCAL_PURGE_OS_TRASH_DAYS:-30}"
OS_TRASH_DIR="${BITPOD_OS_TRASH_DIR:-$HOME/.Trash}"

EXECUTE=0
TODAY_UTC="$(date -u +%F)"

if [[ "${1:-}" == "--execute" ]]; then
  EXECUTE=1
elif [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
  cat <<EOF
Usage: $(basename "$0") [--execute]

Report mode (default):
- checks age-based cleanup transitions and prints planned moves

Execute mode:
- performs moves for eligible items
EOF
  exit 0
fi

if [[ ! -f "$CONTRACT_FILE" ]]; then
  echo "error: missing contract file: $CONTRACT_FILE" >&2
  exit 1
fi

contract_values="$(
python3 - "$CONTRACT_FILE" "$PROFILE" <<'PY'
import shlex
import sys
try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

contract_path = sys.argv[1]
profile = sys.argv[2]
with open(contract_path, "rb") as fh:
    data = tomllib.load(fh)
aliases = data.get("profile_aliases", {})
profile = aliases.get(profile, profile)
profiles = data.get("profiles", {})
if profile not in profiles:
    raise SystemExit(f"profile not found: {profile}")
required = profiles[profile].get("required_paths", [])
optional = profiles[profile].get("optional_paths", [])
allowed = sorted({p.split("/", 1)[0] for p in required + optional})
print("PROFILE_RESOLVED=" + shlex.quote(profile))
print("ALLOWED_DIRECT=" + shlex.quote("|".join(allowed)))
PY
)"
eval "$contract_values"

LOCAL_WORKSPACE="$ROOT/local-workspace"
TRASH_ROOT="$LOCAL_WORKSPACE/local-trash-delete"
PURGE_ROOT="$TRASH_ROOT/local-purge"

if [[ ! -d "$LOCAL_WORKSPACE" ]]; then
  echo "error: local-workspace missing: $LOCAL_WORKSPACE" >&2
  exit 1
fi

mkdir -p "$TRASH_ROOT" "$PURGE_ROOT"

is_allowed_child() {
  local child="$1"
  local allowed="${ALLOWED_DIRECT:-}"
  local item
  IFS='|' read -r -a arr <<< "$allowed"
  for item in "${arr[@]}"; do
    [[ "$child" == "$item" ]] && return 0
  done
  return 1
}

is_older_than_days() {
  local path="$1"
  local days="$2"
  find "$path" -prune -mtime +"$days" | grep -q .
}

unique_path() {
  local target="$1"
  if [[ ! -e "$target" ]]; then
    printf '%s\n' "$target"
    return
  fi
  local n=1
  while [[ -e "${target}-${n}" ]]; do
    n=$((n + 1))
  done
  printf '%s\n' "${target}-${n}"
}

move_or_plan() {
  local src="$1"
  local dst="$2"
  if [[ "$EXECUTE" -eq 1 ]]; then
    mkdir -p "$(dirname "$dst")"
    dst="$(unique_path "$dst")"
    mv "$src" "$dst"
    echo "executed: mv $src -> $dst"
  else
    echo "plan: mv $src -> $dst"
  fi
}

profile_is_lean=0
if [[ "$PROFILE_RESOLVED" == "taylor01_execution_hq_lean" ]]; then
  profile_is_lean=1
fi

prohibited_candidates=0
prohibited_swept=0
trash_candidates=0
trash_promoted=0
purge_candidates=0
purge_moved=0

while IFS= read -r child; do
  [[ -z "$child" ]] && continue
  name="$(basename "$child")"
  if is_allowed_child "$name"; then
    continue
  fi
  prohibited_candidates=$((prohibited_candidates + 1))
  if is_older_than_days "$child" "$PROHIBITED_DAYS"; then
    dest="$TRASH_ROOT/local-prohibited-path-sweep-$TODAY_UTC/$name"
    move_or_plan "$child" "$dest"
    prohibited_swept=$((prohibited_swept + 1))
  else
    echo "hold: prohibited path not old enough: $child"
  fi
done < <(find "$LOCAL_WORKSPACE" -mindepth 1 -maxdepth 1 -type d | sort)

while IFS= read -r bucket; do
  [[ -z "$bucket" ]] && continue
  [[ "$(basename "$bucket")" == "local-purge" ]] && continue
  trash_candidates=$((trash_candidates + 1))
  stale_count="$(find "$bucket" -type f -mtime +"$TRASH_TO_PURGE_DAYS" 2>/dev/null | wc -l | tr -d ' ')"
  if [[ "${stale_count:-0}" -gt 0 ]]; then
    dest="$PURGE_ROOT/$(basename "$bucket")"
    move_or_plan "$bucket" "$dest"
    trash_promoted=$((trash_promoted + 1))
  else
    echo "hold: trash bucket not old enough: $bucket"
  fi
done < <(find "$TRASH_ROOT" -mindepth 1 -maxdepth 1 -type d | sort)

while IFS= read -r file_path; do
  [[ -z "$file_path" ]] && continue
  purge_candidates=$((purge_candidates + 1))
  if [[ "$profile_is_lean" -eq 1 ]]; then
    if [[ "$EXECUTE" -eq 1 ]]; then
      mkdir -p "$OS_TRASH_DIR"
      dest="$OS_TRASH_DIR/$(basename "$file_path")"
      dest="$(unique_path "$dest")"
      mv "$file_path" "$dest"
      echo "executed: mv $file_path -> $dest"
      purge_moved=$((purge_moved + 1))
    else
      echo "plan: os-trash $file_path -> $OS_TRASH_DIR/"
    fi
  else
    echo "reminder: stale local-purge file needs manual delete (human profile): $file_path"
  fi
done < <(find "$PURGE_ROOT" -type f -mtime +"$PURGE_TO_OS_TRASH_DAYS" 2>/dev/null | sort)

echo
echo "Cleanup retention summary"
echo "- profile=$PROFILE_RESOLVED"
echo "- mode=$( [[ "$EXECUTE" -eq 1 ]] && echo EXECUTE || echo REPORT )"
echo "- prohibited_days=$PROHIBITED_DAYS"
echo "- trash_to_purge_days=$TRASH_TO_PURGE_DAYS"
echo "- purge_to_os_trash_days=$PURGE_TO_OS_TRASH_DAYS"
echo "- prohibited_candidates=$prohibited_candidates"
echo "- prohibited_swept=$prohibited_swept"
echo "- trash_candidates=$trash_candidates"
echo "- trash_promoted_to_purge=$trash_promoted"
echo "- purge_candidates=$purge_candidates"
echo "- purge_moved_to_os_trash=$purge_moved"
if [[ "$profile_is_lean" -eq 0 && "$purge_candidates" -gt 0 ]]; then
  echo "- note=human-machine profile uses reminder-only for stale local-purge files"
fi
