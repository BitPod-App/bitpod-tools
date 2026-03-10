#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

overall="PASS"
report_lines=()

run_required() {
  local cmd="$1"
  local label="$2"
  if eval "$cmd" >/tmp/bitpod_eval_cmd.log 2>&1; then
    report_lines+=("- \`$cmd\` -> PASS")
  else
    report_lines+=("- \`$cmd\` -> FAIL")
    overall="FAIL"
    cat /tmp/bitpod_eval_cmd.log >&2
  fi
}

run_optional() {
  local path="$1"
  local cmd="$2"
  if [[ -f "$path" ]]; then
    if eval "$cmd" >/tmp/bitpod_eval_cmd.log 2>&1; then
      report_lines+=("- \`$cmd\` -> PASS")
    else
      report_lines+=("- \`$cmd\` -> FAIL")
      overall="FAIL"
      cat /tmp/bitpod_eval_cmd.log >&2
    fi
  else
    report_lines+=("- \`$cmd\` -> WARN (not present)")
    if [[ "$overall" == "PASS" ]]; then
      overall="PASS_WITH_WARNINGS"
    fi
  fi
}

run_required "python3 -m unittest linear/tests/test_engine.py linear/tests/test_runtime.py linear/tests/test_e2e_flow.py" "core tests"
run_required "bash linear/scripts/local_smoke.sh" "local smoke"
run_optional "$ROOT/linear/scripts/validate_runtime_contract_artifacts.py" "python3 linear/scripts/validate_runtime_contract_artifacts.py"
run_optional "$ROOT/linear/scripts/validate_memory_proposal.py" "python3 linear/scripts/validate_memory_proposal.py"
run_optional "$ROOT/linear/scripts/validate_governance_policy.py" "python3 linear/scripts/validate_governance_policy.py"

printf '# Eval Regression Report\n\n' 
printf -- '- Overall result: %s\n\n' "$overall"
printf '## Checks\n'
printf '%s\n' "${report_lines[@]}"

if [[ "$overall" == "FAIL" ]]; then
  exit 1
fi
