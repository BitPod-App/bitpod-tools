#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DEFAULT="$(cd -- "$SCRIPT_DIR/../.." && pwd)"
ROOT="${BITPOD_APP_ROOT:-${WORKSPACE:-$ROOT_DEFAULT}}"
AUDIT_CTL="$ROOT/bitpod-tools/audit_ctl.sh"
REGISTRY_REFRESH="$ROOT/bitpod-tools/scripts/refresh_repo_registry.sh"
ROOT_HEALTH="$ROOT/bitpod-tools/scripts/check_umbrella_root_health.sh"
REGISTRY_FILE="${BITPOD_REPO_REGISTRY_FILE:-$ROOT/bitpod-tools/config/repo_registry.tsv}"

usage() {
  cat <<EOF
Usage:
  $(basename "$0") repos
  $(basename "$0") status
  $(basename "$0") t3-repos
  $(basename "$0") t3-full
  $(basename "$0") root-health
  $(basename "$0") refresh-registry

Commands:
  repos             Print active repo rows from the umbrella repo registry.
  status            Run the fast umbrella status view (advisory T1 cleanup).
  t3-repos          Run authoritative repo-only umbrella parity.
  t3-full           Run authoritative full T3 audit.
  root-health       Check repo-agnostic root-thread prerequisites for the umbrella root.
  refresh-registry  Refresh the umbrella repo registry from current child repos.

Environment:
  BITPOD_APP_ROOT or WORKSPACE may be used to override the umbrella root.
EOF
}

require_file() {
  local path="$1"
  local label="$2"
  if [[ ! -f "$path" ]]; then
    echo "[workspace_ctl] missing $label: $path" >&2
    exit 1
  fi
}

cmd="${1:-}"
case "$cmd" in
  repos)
    require_file "$REGISTRY_FILE" "repo registry"
    awk -F'|' '
      $0 !~ /^#/ && NF >= 7 && $5 == "1" {
        printf "%s\t%s\tverified=%s\tnotes=%s\n", $1, $2, $6, $7
      }
    ' "$REGISTRY_FILE"
    ;;
  status)
    require_file "$AUDIT_CTL" "audit_ctl"
    BITPOD_APP_ROOT="$ROOT" bash "$AUDIT_CTL" "run audit"
    ;;
  t3-repos)
    require_file "$AUDIT_CTL" "audit_ctl"
    BITPOD_APP_ROOT="$ROOT" bash "$AUDIT_CTL" "run T3 audit only repos"
    ;;
  t3-full)
    require_file "$AUDIT_CTL" "audit_ctl"
    BITPOD_APP_ROOT="$ROOT" bash "$AUDIT_CTL" "run T3 audit"
    ;;
  root-health)
    require_file "$ROOT_HEALTH" "check_umbrella_root_health"
    BITPOD_APP_ROOT="$ROOT" bash "$ROOT_HEALTH"
    ;;
  refresh-registry)
    require_file "$REGISTRY_REFRESH" "refresh_repo_registry"
    BITPOD_APP_ROOT="$ROOT" bash "$REGISTRY_REFRESH"
    ;;
  ""|-h|--help|help)
    usage
    ;;
  *)
    echo "[workspace_ctl] unknown command: $cmd" >&2
    usage >&2
    exit 1
    ;;
esac
