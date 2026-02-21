#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [[ ! -f ".env" ]]; then
  echo "Bridge GPT | FAIL: missing .env at $SCRIPT_DIR/.env"
  exit 1
fi

set -a
source .env
set +a

SESSION="quick-test-$(date +%s)"
FAILED=0
PING_OK=0

run_step() {
  local label="$1"
  shift
  local output
  local status

  echo "Bridge GPT | Step: $label"
  set +e
  output="$("$@" 2>&1)"
  status=$?
  set -e

  if [[ -n "$output" ]]; then
    echo "$output"
  fi

  if [[ $status -ne 0 ]]; then
    echo "Bridge GPT | Step failed: $label"
    FAILED=1
  fi

  return $status
}

run_step "start bridge" ./bridge_ctl.sh start --session "$SESSION" || true
run_step "kickoff session" ./bridge_chat.sh chat "~session Quick GPT smoke test ($SESSION)" || true

PING_OUTPUT=""
echo "Bridge GPT | Step: gpt ping"
set +e
PING_OUTPUT="$(./bridge_chat.sh chat "~gpt reply with exactly: pong" 2>&1)"
PING_STATUS=$?
set -e
echo "$PING_OUTPUT"
if [[ $PING_STATUS -ne 0 ]]; then
  echo "Bridge GPT | Step failed: gpt ping"
  FAILED=1
fi
if echo "$PING_OUTPUT" | grep -Eiq '^GPT:.*pong'; then
  PING_OK=1
fi

run_step "end session" ./bridge_chat.sh chat "~end" || true
run_step "bridge status" ./bridge_ctl.sh status || true

if [[ $FAILED -eq 0 && $PING_OK -eq 1 ]]; then
  echo "Bridge GPT | QUICK TEST: PASS"
  exit 0
fi

echo "Bridge GPT | QUICK TEST: FAIL"
if [[ $PING_OK -ne 1 ]]; then
  echo "Bridge GPT | Reason: ping response did not include 'pong'"
fi
exit 1
