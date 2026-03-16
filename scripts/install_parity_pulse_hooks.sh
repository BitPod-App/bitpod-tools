#!/usr/bin/env bash
set -euo pipefail

ROOT="/Users/cjarguello/bitpod-app"
EMIT_SCRIPT="$ROOT/bitpod-tools/scripts/parity_pulse_emit.sh"

if [[ ! -x "$EMIT_SCRIPT" ]]; then
  chmod +x "$EMIT_SCRIPT"
fi

find "$ROOT" -maxdepth 1 -mindepth 1 -type d | while IFS= read -r repo; do
  [[ -d "$repo/.git" ]] || continue

  for hook in post-commit post-merge pre-push post-checkout; do
    hook_path="$repo/.git/hooks/$hook"
    cat > "$hook_path" <<EOF
#!/usr/bin/env bash
set -euo pipefail
"$EMIT_SCRIPT" "$hook" "$repo" || true
EOF
    chmod +x "$hook_path"
  done
done

echo "Installed parity-pulse hooks into real repos under $ROOT"
