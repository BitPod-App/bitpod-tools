#!/usr/bin/env bash
set -euo pipefail
ROOT="${BITPOD_APP_ROOT:-/Users/cjarguello/BitPod-App}"
exec python3 "$ROOT/bitpod-tools/scripts/linear_temporal_lifecycle_audit.py" "$@"
