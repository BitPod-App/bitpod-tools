#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "$SCRIPT_DIR/../.." && pwd)"
RUNTIME_ENV="${VERA_QA_GATE_RUNTIME_ENV:-$HOME/.hermes/profiles/vera/vera-qa-gate-runtime.env}"

if [[ ! -f "$RUNTIME_ENV" ]]; then
  echo "missing Vera QA Gate runtime env: $RUNTIME_ENV" >&2
  echo "run: python3 linear/scripts/refresh_vera_qa_gate_runtime_env.py" >&2
  exit 1
fi

# shellcheck disable=SC1090
source "$RUNTIME_ENV"

export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"

cd "$REPO_ROOT"
exec python3 linear/src/service.py
