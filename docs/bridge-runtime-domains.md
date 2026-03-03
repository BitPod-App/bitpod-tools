# Bridge Runtime Domains (Legacy + New)

## Purpose

Define the canonical runtime paths and endpoint behavior for Bridge GPT across legacy and new BitPod layouts.

## Canonical Local Runtime Path

- Preferred: `/Users/cjarguello/bitpod-app/bitpod-tools/gpt_bridge`
- Legacy compatibility path (if present): `/Users/cjarguello/bitpod-app/tools/gpt_bridge`

## Endpoint Modes

1. Local mode
- Run local bridge with `./bridge_ctl.sh start --session team`.
- Use local endpoint (`http://127.0.0.1:8787/ask`) unless `GPT_BRIDGE_URL` is set.

2. Remote-managed mode
- Set `GPT_BRIDGE_URL` to remote `/ask` endpoint.
- `bridge_ctl.sh start` is not required for per-message relay in this mode.

## Required Environment

- `OPENAI_API_KEY`
- `GPT_BRIDGE_TOKEN` and/or `GPT_BRIDGE_SHARED_SECRET`

## Host/Path Resolution Order

When callers need to locate Bridge locally, resolve in this order:

1. `BITPOD_GPT_BRIDGE_ROOT` (explicit override)
2. `GPT_BRIDGE_ROOT` (compat override)
3. `/Users/cjarguello/bitpod-app/bitpod-tools/gpt_bridge`
4. `/Users/cjarguello/bitpod-app/tools/gpt_bridge`

## Smoke Tests

```bash
cd /Users/cjarguello/bitpod-app/bitpod-tools/gpt_bridge
set -a; source .env; set +a
./bridge_ctl.sh status
./bridge_chat.sh chat "~gpt reply exactly ack"
```

Remote endpoint check:

```bash
curl -sS -o /tmp/bridge_check.json -w "%{http_code}\n" https://gpt-bridge.bitpod.app/ask \
  -H "Authorization: Bearer $GPT_BRIDGE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"task_type":"general","message":"reply exactly ack","context":[],"constraints":{"json_only":true,"max_tokens":60}}'
cat /tmp/bridge_check.json
```

## Command Intent Surface

- `~decide`/`/decide` remains a valid intent command surface (product-level intent retained).
- Current router behavior may map this intent through existing team/GPT paths until dedicated decision-mode behavior is finalized.
- Core operational commands remain: `~gpt`, `~codex`, `~taylor`, `~session`, `~sync`, `~end`.

## Migration Notes

- Keep legacy path references only as compatibility hints.
- New docs/automation should always use `bitpod-tools/gpt_bridge`.
