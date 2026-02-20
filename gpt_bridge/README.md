# GPT Bridge (B1)

Local HTTP bridge so Codex workflows can call GPT directly.

## Files

- `gpt_bridge.py`: local HTTP service (`POST /ask`)
- `schemas.py`: request/response schema classes
- `ask_gpt.py`: CLI wrapper (JSON to stdout)
- `ask_gpt.sh`: shell wrapper for easy scripting
- `config.example.env`: env var reference
- `logs/`: JSONL request/response logs (`logs/bridge.jsonl`)

## Setup

1. Go to folder:

```bash
cd /Users/cjarguello/bitpod-app/tools/gpt_bridge
```

2. Create local env file from template:

```bash
cp config.example.env .env
```

3. Set values in `.env`:

- `OPENAI_API_KEY` (required)
- `GPT_BRIDGE_TOKEN` and/or `GPT_BRIDGE_SHARED_SECRET` (at least one required)

4. Export env (example):

```bash
set -a
source .env
set +a
```

## Model selection

Default model behavior:

- `general` and `report` route to `gpt-5.2`
- `qa_check` and `score_check` route to `gpt-5-mini`

Per-request override:

- Set `constraints.model` in HTTP payload, or use wrapper `--model`.
- Example:

```bash
./ask_gpt.sh --model gpt-5.2-codex "review this patch"
```

## Run service

```bash
python3 gpt_bridge.py
```

Service binds only to `127.0.0.1` and rejects startup on any other host.

## HTTP usage

```bash
curl -sS -X POST "http://127.0.0.1:8787/ask" \
  -H "Authorization: Bearer $GPT_BRIDGE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "general",
    "message": "ping",
    "context": [],
    "constraints": {"json_only": true, "max_tokens": 300},
    "meta": {"repo": "bitpod"}
  }'
```

Override model in HTTP:

```bash
curl -sS -X POST "http://127.0.0.1:8787/ask" \
  -H "Authorization: Bearer $GPT_BRIDGE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "general",
    "message": "Use stronger reasoning",
    "constraints": {"json_only": true, "model": "gpt-5.2"}
  }'
```

## CLI wrapper usage

Simple:

```bash
./ask_gpt.sh "ping"
```

With context file:

```bash
./ask_gpt.sh --context-file /tmp/snippet.txt "Summarize this"
```

With piped context:

```bash
git diff | ./ask_gpt.sh --context-stdin "Review this diff"
```

With explicit model override:

```bash
./ask_gpt.sh --model gpt-5.2 "analyze this"
```

Optional env vars for wrapper:

- `GPT_BRIDGE_URL` (default `http://127.0.0.1:8787/ask`)
- `GPT_BRIDGE_TOKEN` (bearer token)
- `GPT_BRIDGE_SHARED_SECRET` (fallback header)

## Response contract

`POST /ask` returns a `GPTResponse` JSON object:

- `status`: `ok | needs_info | blocked`
- `answer.json`: object (always present)
- `answer.markdown`: optional string
- `warnings`: array of strings
- `followups_for_codex`: array of strings
- `trace`: includes `request_id`, `model`, and token usage (if available)

## Logging

Each request/response is appended as JSONL to:

- `logs/bridge.jsonl`

Each record includes timestamp and request ID.

## Basic smoke checks (B1)

1. Start server in one terminal:

```bash
python3 gpt_bridge.py
```

2. Valid auth returns `GPTResponse`:

```bash
./ask_gpt.sh "ping"
```

3. Missing auth returns 401:

```bash
env -u GPT_BRIDGE_TOKEN -u GPT_BRIDGE_SHARED_SECRET ./ask_gpt.sh "ping"
```
