#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [[ -f .env ]]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

BRIDGE_URL="${GPT_BRIDGE_URL:-http://127.0.0.1:8787/ask}"
START_LOG="${GPT_BRIDGE_START_LOG:-$SCRIPT_DIR/logs/bridge_start.log}"

check_bridge() {
  local code
  code="$(curl -s -m 2 -o /dev/null -w "%{http_code}" \
    -X POST "$BRIDGE_URL" \
    -H "Content-Type: application/json" \
    -d '{"task_type":"general","message":"ping","context":[],"constraints":{"json_only":true,"max_tokens":10},"meta":{}}' 2>/dev/null || true)"
  [[ "$code" != "000" ]]
}

bridge_host() {
  local host
  host="$(printf '%s' "$BRIDGE_URL" | sed -nE 's#^[a-zA-Z]+://([^/:]+).*#\1#p')"
  if [[ -z "${host:-}" ]]; then
    host="127.0.0.1"
  fi
  printf '%s' "$host"
}

is_local_bridge_url() {
  local host
  host="$(bridge_host)"
  [[ "$host" == "127.0.0.1" || "$host" == "localhost" || "$host" == "::1" ]]
}

if ! check_bridge; then
  if is_local_bridge_url; then
    # Delegate startup to bridge_ctl.sh so start checks and error reporting
    # stay centralized and consistent across callers.
    if ! "$SCRIPT_DIR/bridge_ctl.sh" start >/dev/null 2>&1; then
      echo "Bridge failed to start. See $START_LOG" >&2
      exit 1
    fi
  else
    echo "Remote bridge unreachable: $BRIDGE_URL" >&2
    echo "Start or fix the remote bridge service, then retry." >&2
    exit 1
  fi
fi

if ! check_bridge; then
  echo "Bridge failed to start. See $START_LOG" >&2
  exit 1
fi

if [[ $# -eq 0 ]]; then
  exec "$SCRIPT_DIR/ask_gpt.sh" "ping"
fi
exec "$SCRIPT_DIR/ask_gpt.sh" "$@"
