#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

echo "[1/4] unit tests"
python3 -m unittest linear/tests/test_engine.py linear/tests/test_runtime.py linear/tests/test_e2e_flow.py

echo "[2/4] sample event simulations"
cd linear/src
python3 simulate.py --mode gh_opened --event ../events/sample_pr_opened.json
python3 simulate.py --mode linear_comment --event ../events/sample_linear_comment_passed.json
python3 simulate.py --mode aging_scan --event ../events/sample_aging_scan.json

echo "[3/4] end-to-end lifecycle simulation"
python3 simulate_e2e.py

echo "[4/4] dry-run service boot check"
PYTHONUNBUFFERED=1 BOT_PORT=18787 python3 service.py --dry-run >/tmp/linear_service_boot.log 2>&1 &
svc_pid=$!
sleep 1
kill "$svc_pid" >/dev/null 2>&1 || true
wait "$svc_pid" 2>/dev/null || true
if ! rg -q "listening on http://127.0.0.1:18787" /tmp/linear_service_boot.log; then
  echo "service boot check failed"
  cat /tmp/linear_service_boot.log
  exit 1
fi

echo "local smoke PASS"
