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

: "${OPENAI_API_KEY:?OPENAI_API_KEY is required (set in .env)}"
if [[ -z "${GPT_BRIDGE_TOKEN:-}" && -z "${GPT_BRIDGE_SHARED_SECRET:-}" ]]; then
  echo "Set GPT_BRIDGE_TOKEN or GPT_BRIDGE_SHARED_SECRET in .env" >&2
  exit 1
fi

BRIDGE_URL="${GPT_BRIDGE_URL:-http://127.0.0.1:8787/ask}"
START_LOG="${GPT_BRIDGE_START_LOG:-$SCRIPT_DIR/logs/bridge_start.log}"
PID_FILE="${GPT_BRIDGE_PID_FILE:-$SCRIPT_DIR/logs/bridge.pid}"

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
    mkdir -p "$SCRIPT_DIR/logs"
    nohup python3 "$SCRIPT_DIR/gpt_bridge.py" >>"$START_LOG" 2>&1 &
    echo "$!" > "$PID_FILE"

    for _ in {1..20}; do
      if check_bridge; then
        break
      fi
      sleep 0.25
    done
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
