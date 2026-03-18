#!/usr/bin/env bash
set -euo pipefail

ROOT="${BITPOD_APP_ROOT:-/Users/cjarguello/BitPod-App}"
AUDIT_CTL="$ROOT/bitpod-tools/audit_ctl.sh"
REGISTRY_FILE="${BITPOD_REPO_REGISTRY_FILE:-$ROOT/bitpod-tools/config/repo_registry.tsv}"

event_name="${1:-unknown}"
repo_path="${2:-$(pwd)}"
repo_name="$(basename "$repo_path")"
timestamp="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

if [[ ! -x "$AUDIT_CTL" ]]; then
  echo "[parity pulse hook] audit_ctl.sh not executable at $AUDIT_CTL" >&2
  exit 1
fi

if [[ ! -d "$repo_path/.git" ]]; then
  echo "[parity pulse hook] repo path is not a git repo: $repo_path" >&2
  exit 1
fi

fresh_flag=""
case "$event_name" in
  pre-push|post-push)
    fresh_flag=" fresh"
    ;;
esac

pulse_output="$(
  BITPOD_APP_ROOT="$ROOT" \
  BITPOD_REPO_REGISTRY_FILE="$REGISTRY_FILE" \
  "$AUDIT_CTL" "__parity_pulse__ event=$event_name$fresh_flag"
)"

printf '%s\n' "$pulse_output" >&2
