#!/usr/bin/env bash
set -euo pipefail

ROOT="/Users/cjarguello/bitpod-app"
AUDIT_CTL="$ROOT/bitpod-tools/audit_ctl.sh"
PULSE_ROOT="$ROOT/local-workspace/local-working-files/local-parity-pulse"

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

mkdir -p "$PULSE_ROOT/$repo_name"

fresh_flag=""
case "$event_name" in
  pre-push|post-push)
    fresh_flag=" fresh"
    ;;
esac

pulse_output="$("$AUDIT_CTL" "__parity_pulse__ event=$event_name$fresh_flag")"

latest_file="$PULSE_ROOT/$repo_name/latest.md"
history_file="$PULSE_ROOT/$repo_name/history.log"

{
  echo "# Parity Pulse"
  echo
  echo "- timestamp: $timestamp"
  echo "- repo: $repo_name"
  echo "- event: $event_name"
  echo
  printf '%s\n' "$pulse_output"
} > "$latest_file"

{
  echo "=== $timestamp repo=$repo_name event=$event_name ==="
  printf '%s\n' "$pulse_output"
  echo
} >> "$history_file"

printf '%s\n' "$pulse_output" >&2
