#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "usage: $0 /ABS/PATH/clone_root /ABS/PATH/report.md" >&2
  exit 2
fi

CLONE_ROOT="$1"
OUT="$2"
TS="$(date -u +"%Y-%m-%d %H:%M:%SZ")"
DOC_PROBE="${HOME}/Documents/.scope_should_fail"
CLONE_PROBE="${CLONE_ROOT}/.scope_write_test"

mkdir -p "$(dirname "$OUT")"

run_probe() {
  local label="$1"
  local expected="$2"
  local cmd="$3"
  local observed
  if bash -lc "$cmd" >/dev/null 2>&1; then
    observed="allowed"
  else
    observed="denied"
  fi
  printf '| %s | %s | %s |\n' "$label" "$expected" "$observed"
}

{
  echo "# Post-Bootstrap Scope Probe"
  echo
  echo "- UTC: ${TS}"
  echo "- Clone root: \`${CLONE_ROOT}\`"
  echo
  echo "## Probe Results"
  echo
  echo "| Probe | Expected after hardening | Observed |"
  echo "|---|---|---|"
  run_probe "Write inside clone root" "allowed" "touch '${CLONE_PROBE}' && rm -f '${CLONE_PROBE}'"
  run_probe "Read ~/.zshrc" "denied" "head -n 1 '${HOME}/.zshrc'"
  if [[ -d "${HOME}/Documents" ]]; then
    run_probe "Write ~/Documents" "denied" "touch '${DOC_PROBE}' && rm -f '${DOC_PROBE}'"
  else
    echo "| Write ~/Documents | denied | unverifiable (~/Documents missing) |"
  fi
  echo
  echo "## Interpretation"
  echo
  echo "- If either outside-path probe is \`allowed\`, local scope hardening is not complete."
  echo "- Opening Codex on one workspace path is not a strong isolation boundary by itself."
  echo "- Strong local isolation requires a dedicated macOS user/profile with no personal mounts."
} > "$OUT"

echo "WROTE_REPORT ${OUT}"
