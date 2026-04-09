#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DEFAULT="$(cd -- "$SCRIPT_DIR/../.." && pwd)"
ROOT="${BITPOD_APP_ROOT:-${WORKSPACE:-$ROOT_DEFAULT}}"

canonicalize_root_path() {
  local root="$1"
  local parent base canonical
  parent="$(dirname "$root")"
  base="$(basename "$root")"
  canonical="$parent/BitPod-App"

  if [[ "$base" != "BitPod-App" && -e "$canonical" ]]; then
    local root_inode canonical_inode
    root_inode="$(ls -id "$root" | awk '{print $1}')"
    canonical_inode="$(ls -id "$canonical" | awk '{print $1}')"
    if [[ "$root_inode" == "$canonical_inode" ]]; then
      echo "$canonical"
      return 0
    fi
  fi

  echo "$root"
}

ROOT="$(canonicalize_root_path "$ROOT")"

check_path() {
  local label="$1"
  local path="$2"
  if [[ -e "$path" ]]; then
    echo "- check=$label status=PRESENT path=$path"
    return 0
  fi
  echo "- check=$label status=MISSING path=$path"
  return 1
}

print_header() {
  echo "Umbrella Root Health"
  echo "- root=$ROOT"
}

check_case_note() {
  local lower_root
  lower_root="$(dirname "$ROOT")/$(basename "$ROOT" | tr '[:upper:]' '[:lower:]')"
  if [[ "$lower_root" != "$ROOT" && -e "$lower_root" ]]; then
    local root_inode lower_inode
    root_inode="$(ls -id "$ROOT" | awk '{print $1}')"
    lower_inode="$(ls -id "$lower_root" | awk '{print $1}')"
    if [[ "$root_inode" == "$lower_inode" ]]; then
      echo "- canonical_root=$ROOT"
      echo "- compatibility_alias=$lower_root"
      echo "- path_case_note=case-insensitive alias to canonical root"
      return 0
    fi
    echo "- canonical_root=$ROOT"
    echo "- conflicting_root_alias=$lower_root"
    echo "- path_case_note=separate lowercase path exists; investigate manually"
    return 0
  fi
  echo "- canonical_root=$ROOT"
  echo "- path_case_note=no lowercase compatibility alias detected"
}

main() {
  local failures=0

  print_header
  check_case_note

  echo
  echo "Checks"

  check_path "root_agents" "$ROOT/AGENTS.md" || failures=$((failures + 1))
  check_path "root_codex_dir" "$ROOT/.codex" || failures=$((failures + 1))
  check_path "root_codex_agents" "$ROOT/.codex/AGENTS.md" || failures=$((failures + 1))
  check_path "root_codex_config" "$ROOT/.codex/config.toml" || failures=$((failures + 1))
  check_path "root_org_workspace" "$ROOT/.codex/org-workspace.toml" || failures=$((failures + 1))
  check_path "root_environment" "$ROOT/.codex/environments/environment.toml" || failures=$((failures + 1))
  check_path "policy_canon" "$ROOT/bitpod-docs/policies/taylored-policy.md" || failures=$((failures + 1))
  check_path "policy_rules" "$ROOT/bitpod-docs/policies/taylored-policy-rules.md" || failures=$((failures + 1))
  check_path "policy_registry" "$ROOT/bitpod-docs/policies/policy-registry.toml" || failures=$((failures + 1))

  echo
  echo "Result"
  if [[ "$failures" -eq 0 ]]; then
    echo "- overall=OK"
    echo "- detail=Umbrella root thread prerequisites are present."
    exit 0
  fi

  echo "- overall=BROKEN"
  echo "- missing_count=$failures"
  echo "- recommended_fix=bash \"$ROOT/bitpod-tools/scripts/bootstrap_org_workspace.sh\" --root \"$ROOT\" --profile <profile> --skip-clone"
  exit 1
}

main "$@"
