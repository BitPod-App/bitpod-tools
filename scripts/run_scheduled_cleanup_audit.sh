#!/usr/bin/env bash
set -euo pipefail

ROOT="${BITPOD_APP_ROOT:-/Users/cjarguello/BitPod-App}"
AUDIT_CTL="$ROOT/bitpod-tools/audit_ctl.sh"
STATE_DIR="$ROOT/local-workspace/local-working-files/local-cleanup-audit"
STATE_FILE="$STATE_DIR/scheduled_cleanup_state.env"
LATEST_REPORT="$STATE_DIR/latest_scheduled_cleanup.md"
LINEAR_PAYLOAD="$STATE_DIR/latest_linear_escalation.md"
TIMESTAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

mkdir -p "$STATE_DIR"

consecutive_failures=0
last_pass_at=""
last_run_at=""
last_result=""
next_due_at=""

if [[ -f "$STATE_FILE" ]]; then
  # shellcheck disable=SC1090
  source "$STATE_FILE"
fi

report=""
run_exit=0
if report="$(
  BITPOD_APP_ROOT="$ROOT" \
  "$AUDIT_CTL" "run T3 audit"
)"; then
  run_exit=0
else
  run_exit=$?
fi

{
  echo "# Scheduled Cleanup Audit"
  echo
  echo "- timestamp: $TIMESTAMP"
  echo "- mode: scheduled-report-only"
  echo "- command: run T3 audit"
  echo "- exit_code: $run_exit"
  echo
  printf '%s\n' "$report"
} > "$LATEST_REPORT"

if printf '%s\n' "$report" | grep -q -- "result=PORCELAIN"; then
  last_result="PORCELAIN"
  last_pass_at="$TIMESTAMP"
  consecutive_failures=0
else
  last_result="FRACTURED"
  consecutive_failures=$((consecutive_failures + 1))
fi

last_run_at="$TIMESTAMP"
next_due_at="$(date -u -v+14d +%Y-%m-%dT%H:%M:%SZ)"

issue_kind="Chore"
issue_priority="low"
if [[ "$consecutive_failures" -eq 2 ]]; then
  issue_priority="normal"
elif [[ "$consecutive_failures" -eq 3 ]]; then
  issue_priority="high"
elif [[ "$consecutive_failures" -ge 4 ]]; then
  issue_kind="Bug"
  issue_priority="urgent"
fi

if [[ "$last_result" == "FRACTURED" ]]; then
  {
    echo "# Scheduled Cleanup Escalation Payload"
    echo
    echo "- timestamp: $TIMESTAMP"
    echo "- issue_kind: $issue_kind"
    echo "- issue_priority: $issue_priority"
    echo "- consecutive_failures: $consecutive_failures"
    echo "- latest_report: $LATEST_REPORT"
    echo
    echo "This payload is generated fail-closed."
    echo
    echo "Direct Linear mutation is not performed here unless a dedicated executor"
    echo "is wired and approved. Use this payload to update the single rolling"
    echo "scheduled cleanup issue."
  } > "$LINEAR_PAYLOAD"
else
  {
    echo "# Scheduled Cleanup Escalation Payload"
    echo
    echo "- timestamp: $TIMESTAMP"
    echo "- state: reset"
    echo "- latest_report: $LATEST_REPORT"
    echo
    echo "The latest scheduled cleanup passed. Reset any rolling failure issue"
    echo "state instead of escalating it."
  } > "$LINEAR_PAYLOAD"
fi

cat > "$STATE_FILE" <<EOF
consecutive_failures=$consecutive_failures
last_pass_at="$last_pass_at"
last_run_at="$last_run_at"
last_result="$last_result"
next_due_at="$next_due_at"
EOF

printf '%s\n' "$report"
