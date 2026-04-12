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
PID_FILE="${GPT_BRIDGE_PID_FILE:-$SCRIPT_DIR/logs/bridge.pid}"
START_LOG="${GPT_BRIDGE_START_LOG:-$SCRIPT_DIR/logs/bridge_start.log}"
SESSION="default"

usage() {
  cat <<'EOF'
Usage:
  bridge_ctl.sh start [--session <id>]
  bridge_ctl.sh status
  bridge_ctl.sh stop [--session <id>]
EOF
}

if [[ $# -lt 1 ]]; then
  usage
  exit 2
fi

ACTION="$1"
shift

while [[ $# -gt 0 ]]; do
  case "$1" in
    --session)
      if [[ $# -lt 2 ]]; then
        echo "Missing value for --session" >&2
        exit 2
      fi
      SESSION="$2"
      shift 2
      ;;
    *)
      echo "Unknown arg: $1" >&2
      usage
      exit 2
      ;;
  esac
done

check_bridge() {
  local health_url code
  if [[ "$BRIDGE_URL" == */ask ]]; then
    health_url="${BRIDGE_URL%/ask}/health"
  else
    health_url="${BRIDGE_URL%/}/health"
  fi
  code="$(curl -s -m 2 -o /dev/null -w "%{http_code}" "$health_url" 2>/dev/null || true)"
  [[ "$code" == "200" ]]
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

bridge_port() {
  local port
  port="$(printf '%s' "$BRIDGE_URL" | sed -nE 's#.*:([0-9]+)/.*#\1#p')"
  if [[ -z "${port:-}" ]]; then
    port="8787"
  fi
  printf '%s' "$port"
}

emit_chat() {
  local text="$1"
  if [[ -x "$SCRIPT_DIR/bridge_chat.sh" ]]; then
    "$SCRIPT_DIR/bridge_chat.sh" post --session "$SESSION" --from system "$text" >/dev/null 2>&1 || true
  fi
}

start_bridge() {
  if check_bridge; then
    echo "Bridge GPT | Active"
    return 0
  fi

  if ! is_local_bridge_url; then
    echo "Bridge GPT | Start skipped (remote managed endpoint: $BRIDGE_URL)" >&2
    echo "Bridge GPT | Ensure the remote bridge service is running." >&2
    return 1
  fi

  : "${OPENAI_API_KEY:?OPENAI_API_KEY is required (set in .env)}"
  if [[ -z "${GPT_BRIDGE_TOKEN:-}" && -z "${GPT_BRIDGE_SHARED_SECRET:-}" ]]; then
    echo "Set GPT_BRIDGE_TOKEN or GPT_BRIDGE_SHARED_SECRET in .env" >&2
    return 1
  fi

  mkdir -p "$SCRIPT_DIR/logs"
  nohup python3 "$SCRIPT_DIR/gpt_bridge.py" >>"$START_LOG" 2>&1 &
  echo "$!" > "$PID_FILE"

  for _ in {1..20}; do
    if check_bridge; then
      echo "Bridge GPT | Active"
      emit_chat "GPT Bridge joined the chat"
      return 0
    fi
    sleep 0.25
  done

  echo "Bridge GPT | Start failed (see $START_LOG)" >&2
  return 1
}

stop_bridge() {
  if ! is_local_bridge_url; then
    echo "Bridge GPT | Stop skipped (remote managed endpoint: $BRIDGE_URL)"
    return 0
  fi

  local stopped=0
  if [[ -f "$PID_FILE" ]]; then
    local pid
    pid="$(cat "$PID_FILE" 2>/dev/null || true)"
    if [[ -n "${pid:-}" ]] && kill -0 "$pid" 2>/dev/null; then
      kill "$pid" 2>/dev/null || true
      for _ in {1..20}; do
        if ! kill -0 "$pid" 2>/dev/null; then
          stopped=1
          break
        fi
        sleep 0.1
      done
      if kill -0 "$pid" 2>/dev/null; then
        kill -9 "$pid" 2>/dev/null || true
        stopped=1
      fi
    fi
    rm -f "$PID_FILE"
  fi

  # Fallback for bridge processes not tracked by PID file.
  if check_bridge; then
    local port
    port="$(bridge_port)"
    local pids
    pids="$(lsof -tiTCP:"$port" -sTCP:LISTEN 2>/dev/null || true)"
    if [[ -n "${pids:-}" ]]; then
      while IFS= read -r pid; do
        [[ -z "${pid:-}" ]] && continue
        kill "$pid" 2>/dev/null || true
      done <<<"$pids"
      sleep 0.3
      # Hard kill if still alive on same port.
      pids="$(lsof -tiTCP:"$port" -sTCP:LISTEN 2>/dev/null || true)"
      if [[ -n "${pids:-}" ]]; then
        while IFS= read -r pid; do
          [[ -z "${pid:-}" ]] && continue
          kill -9 "$pid" 2>/dev/null || true
        done <<<"$pids"
      fi
    else
      pkill -f "gpt_bridge.py" 2>/dev/null || true
    fi
    sleep 0.3
    if ! check_bridge; then
      stopped=1
    fi
  fi

  if check_bridge; then
    echo "Bridge GPT | Stop failed (still active)" >&2
    return 1
  fi

  echo "Bridge GPT | Inactive"
  emit_chat "GPT Bridge left the chat"
  return 0
}

status_bridge() {
  if check_bridge; then
    echo "Bridge GPT | Active"
  else
    echo "Bridge GPT | Inactive"
  fi
}

case "$ACTION" in
  start)
    start_bridge
    ;;
  stop)
    stop_bridge
    ;;
  status)
    status_bridge
    ;;
  *)
    usage
    exit 2
    ;;
esac
