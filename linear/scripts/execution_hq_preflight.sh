#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
WORKSPACE_ROOT="$(cd "${ROOT}/.." && pwd)"
AUDIT_CTL="${ROOT}/audit_ctl.sh"
RUN_AUDIT=1

usage() {
  cat <<'EOF'
usage: execution_hq_preflight.sh [--skip-audit]

Checks the MacBook control console for the minimum AI HQ bootstrap prerequisites:
- required local tooling
- GitHub auth
- SSH key presence
- discoverable AI HQ host alias or AI_HQ_HOST env var
- optional Tailscale and 1Password CLI presence
- optional full T3 cleanup gate
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --skip-audit)
      RUN_AUDIT=0
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

status=0

pass() { printf 'PASS %s\n' "$1"; }
warn() { printf 'WARN %s\n' "$1"; }
fail() { printf 'FAIL %s\n' "$1"; status=1; }

require_cmd() {
  local cmd="$1"
  local label="$2"
  if command -v "$cmd" >/dev/null 2>&1; then
    pass "${label}: $(command -v "$cmd")"
  else
    fail "${label}: missing"
  fi
}

detect_ssh_alias() {
  local config="${HOME}/.ssh/config"
  [[ -f "$config" ]] || return 1
  awk '
    BEGIN { IGNORECASE=1 }
    $1 == "Host" {
      for (i = 2; i <= NF; i++) {
        if ($i == "*" || $i ~ /[*?]/) {
          continue
        }
        if ($i ~ /(ai-hq|aihq|macmini|mac-mini|taylorhq|taylor01)/) {
          print $i
          exit
        }
      }
    }
  ' "$config"
}

echo "Execution HQ preflight"
echo "- workspace_root=${WORKSPACE_ROOT}"
echo "- repo_root=${ROOT}"

require_cmd ssh "ssh"
require_cmd git "git"
require_cmd gh "gh"

if command -v op >/dev/null 2>&1; then
  pass "1Password CLI: $(command -v op)"
else
  warn "1Password CLI: missing"
fi

if command -v tailscale >/dev/null 2>&1; then
  pass "Tailscale: $(command -v tailscale)"
else
  warn "Tailscale: missing"
fi

if [[ -f "${HOME}/.ssh/id_ed25519.pub" ]]; then
  pass "SSH public key: ${HOME}/.ssh/id_ed25519.pub"
else
  fail "SSH public key: ${HOME}/.ssh/id_ed25519.pub missing"
fi

if gh auth status >/dev/null 2>&1; then
  pass "GitHub auth: available"
else
  fail "GitHub auth: unavailable"
fi

AI_HQ_TARGET="${AI_HQ_HOST:-}"
if [[ -n "$AI_HQ_TARGET" ]]; then
  pass "AI HQ target: AI_HQ_HOST=${AI_HQ_TARGET}"
else
  AI_HQ_TARGET="$(detect_ssh_alias || true)"
  if [[ -n "$AI_HQ_TARGET" ]]; then
    pass "AI HQ target: ssh alias ${AI_HQ_TARGET}"
  else
    fail "AI HQ target: no AI_HQ_HOST env var and no matching ssh alias found"
  fi
fi

if [[ "$RUN_AUDIT" -eq 1 ]]; then
  echo
  echo "Running full T3 audit..."
  if bash "$AUDIT_CTL" "run T3 audit"; then
    pass "T3 cleanup gate: PORCELAIN"
  else
    fail "T3 cleanup gate: not PORCELAIN"
  fi
fi

echo
if [[ "$status" -eq 0 ]]; then
  echo "Execution HQ preflight PASS"
else
  echo "Execution HQ preflight FAIL"
fi

exit "$status"
