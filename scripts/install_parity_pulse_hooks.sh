#!/usr/bin/env bash
set -euo pipefail

ROOT="${BITPOD_APP_ROOT:-/Users/cjarguello/BitPod-App}"
REGISTRY_FILE="${BITPOD_REPO_REGISTRY_FILE:-$ROOT/bitpod-tools/config/repo_registry.tsv}"
EMIT_SCRIPT="$ROOT/bitpod-tools/scripts/parity_pulse_emit.sh"

if [[ ! -x "$EMIT_SCRIPT" ]]; then
  chmod +x "$EMIT_SCRIPT"
fi

if [[ ! -f "$REGISTRY_FILE" ]]; then
  echo "[install_parity_pulse_hooks] repo registry missing: $REGISTRY_FILE" >&2
  exit 1
fi

while IFS='|' read -r repo rel_path pulse_enabled cleanup_enabled thread_visible verified notes; do
  [[ -z "${repo// }" ]] && continue
  [[ "$repo" =~ ^# ]] && continue
  [[ "${pulse_enabled:-0}" == "1" ]] || continue
  [[ "${verified:-0}" == "1" ]] || continue

  repo_path="$ROOT/$rel_path"
  [[ -d "$repo_path/.git/hooks" ]] || continue

  for hook in post-commit post-merge pre-push post-checkout; do
    hook_path="$repo_path/.git/hooks/$hook"
    cat > "$hook_path" <<EOF
#!/usr/bin/env bash
set -euo pipefail
BITPOD_APP_ROOT="$ROOT" BITPOD_REPO_REGISTRY_FILE="$REGISTRY_FILE" "$EMIT_SCRIPT" "$hook" "$repo_path" || true
EOF
    chmod +x "$hook_path"
  done
done < "$REGISTRY_FILE"

echo "Installed parity-pulse hooks into registry-backed repos under $ROOT"
