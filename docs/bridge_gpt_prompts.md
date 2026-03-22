# Bridge GPT Prompts (Run + Test)

## Runtime Path
- `$WORKSPACE/bitpod-tools/gpt_bridge`

## Start
```bash
cd $WORKSPACE/bitpod-tools/gpt_bridge
set -a; source .env; set +a
./bridge_ctl.sh start --session team
./bridge_ctl.sh status
```

## Chat Router Prompts
```bash
./bridge_chat.sh chat "/help"
./bridge_chat.sh chat "~session Let's plan rollout"
./bridge_chat.sh chat "~gpt reply exactly ack"
./bridge_chat.sh chat "~codex verify bridge health"
./bridge_chat.sh chat "~taylor status"
./bridge_chat.sh chat "~sync"
./bridge_chat.sh chat "~end"
```

## Remote Endpoint Smoke Test
```bash
cd $WORKSPACE/bitpod-tools/gpt_bridge
set -a; source .env; set +a
curl -sS -o /tmp/bridge_check.json -w "%{http_code}\n" https://gpt-bridge.bitpod.app/ask \
  -H "Authorization: Bearer $GPT_BRIDGE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"task_type":"general","message":"reply exactly ack","context":[],"constraints":{"json_only":true,"max_tokens":60}}'
cat /tmp/bridge_check.json
```

## Common Failures
- `OpenAI call failed` + `invalid_api_key`: rotate/fix `OPENAI_API_KEY` in `.env`, restart bridge.
- `401` from `/ask`: wrong/missing `GPT_BRIDGE_TOKEN` in client shell.
- DNS resolution fails for `gpt-bridge.bitpod.app`: tunnel route/DNS not propagated.
