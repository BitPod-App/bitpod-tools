# Cloudflare Migration Path (Taylor Independence)

Goal: keep Taylor logic independent from any single platform.

## Current shape
- `linear/src/engine.py`: core decision logic (platform-neutral actions)
- `linear/src/runtime.py`: orchestration + memory event recording
- `linear/src/service.py`: adapter endpoint for GitHub/Linear payloads

## Migration plan
1. Keep `engine.py` unchanged.
2. Replace `service.py` transport layer with Cloudflare Worker handlers.
3. Swap `InMemoryStore` with durable backend (`KV`/`D1`/external DB).
4. Keep provider/model in env (`LLM_PROVIDER`, `LLM_MODEL`) so runtime is portable.

## Why this avoids lock-in
- Platform-specific webhooks live at adapter edge.
- Core policies/gates remain reusable across Linear/GitHub/Slack/Discord.
- Memory is abstracted via `MemoryStore` interface.
