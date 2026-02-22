# GPT Bridge (B1)

HTTP bridge so Codex workflows can call GPT directly (local or remote-managed endpoint).

## Files

- `gpt_bridge.py`: HTTP service (`POST /ask`)
- `schemas.py`: request/response schema classes
- `ask_gpt.py`: CLI wrapper (JSON to stdout)
- `ask_gpt.sh`: shell wrapper for easy scripting
- `gpt_bridge_mcp.py`: MCP stdio server exposing a tool that forwards to `/ask`
- `bridge_chat.py`: shared chat-log relay (`send`, `post`, `tail`)
- `bridge_chat.sh`: shell wrapper for `bridge_chat.py`
- `bridge_ctl.sh`: bridge lifecycle controls (`start`, `status`, `stop`)
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

## 60-second runbook

START (one time per machine boot/session):

```bash
cd /Users/cjarguello/bitpod-app/tools/gpt_bridge
set -a; source .env; set +a
./bridge_ctl.sh start --session team
cloudflared tunnel run gpt-bridge
```

CHAT (Codex chat):

- `~session <topic>`
- `~gpt <message>`
- `~sync` (manual pull; most new GPT messages are now auto-pulled on your next chat command)
- `~end`

TAYLOR QA (auditable):

- Build a deterministic review bundle first (in repo): `bash scripts/make_review_bundle.sh`
- Send QA request via bridge with enforced header/hash/footer + artifact writes:

```bash
cd /Users/cjarguello/bitpod-app/tools/gpt_bridge
./bridge_chat.sh send "Line-by-line QA review this bundle." \
  --task-type qa_check \
  --taylor-qa \
  --bundle-path /absolute/path/to/review_bundle.md \
  --session pr-review-<id>
```

Hash integrity note:
- `BUNDLE_SHA256` is computed from the exact raw bytes of the bundle file on disk (binary read, no newline normalization, no post-processing).

- Verify QA run (primary path):

```bash
./bridge_verify_qa.sh pr-review-<id>
```

STOP:

```bash
cd /Users/cjarguello/bitpod-app/tools/gpt_bridge
./bridge_ctl.sh stop --session team
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

By default it binds to `127.0.0.1`.
For remote hosting, set:

```bash
export GPT_BRIDGE_ALLOW_NONLOCALHOST=1
export GPT_BRIDGE_HOST=0.0.0.0
```

Then run:

```bash
python3 gpt_bridge.py
```

## Option 2: Remote-managed endpoint (no per-message terminal loop)

Point clients to a shared URL:

```bash
export GPT_BRIDGE_URL="https://your-bridge.example.com/ask"
export GPT_BRIDGE_TOKEN="your_bridge_token"
```

Notes:

- `bridge_ctl.sh start` is local-only; for remote URL it will not spawn a local process.
- `bridge_ctl.sh stop` is local-only; for remote URL it is a no-op.
- `ask_once.sh` will not try to start local bridge when `GPT_BRIDGE_URL` is remote.
- Keep auth enabled (`GPT_BRIDGE_TOKEN` and/or `GPT_BRIDGE_SHARED_SECRET`).

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

## Easy mode (one command)

Use this when you want "start bridge if needed + call GPT" in one step:

```bash
cd /Users/cjarguello/bitpod-app/tools/gpt_bridge
./ask_once.sh "ping"
```

How it works:

- Loads `.env`
- Starts `gpt_bridge.py` automatically if not already running
- Calls `ask_gpt.sh` and prints JSON response

If you run without a message, it defaults to `ping`:

```bash
./ask_once.sh
```

## Shared chat relay (group-chat style)

Use this to simulate chat with shared logs:

```bash
cd /Users/cjarguello/bitpod-app/tools/gpt_bridge
./bridge_chat.sh send "ping"
```

What it does:

- Logs user + GPT events to `logs/chat.jsonl`
- Uses UTC timestamps on each event (in log file)
- Auto-injects latest persistent memory from `logs/memory_store.jsonl` on `send`
- Auto-recovers stale, unfinalized sessions before `send` (default inactivity threshold: 900 seconds)
- Prints timeline lines like:
  - `user: ...`
  - `GPT: ...`
- Prints status events:
  - `Bridge GPT | Checking config...`
  - `Bridge GPT | Starting bridge...`
  - `Bridge GPT | Authenticating...`
  - `Bridge GPT | Sending prompt...`
  - `GPT Bridge | Active`

## How To Prove Taylor QA Ran

Primary path:

```bash
cd /Users/cjarguello/bitpod-app/tools/gpt_bridge
./bridge_verify_qa.sh <session_id>
```

Verifier checks:
- request header in logs (`MODE: TAYLOR_QA`, `CONTRACT_PATH`, `BUNDLE_SHA256`)
- request payload + GPT response presence
- response footer (`TAYLOR_QA_RESULT`, `QA_RUN_ID`, `QA_OUTPUT_PATH`, `BUNDLE_SHA256`)
- hash match between request and response
- QA artifacts on disk (`qa_review.md`, `acceptance_criteria_checklist.md`, `risk_notes.md`)
  - plus `qa_run_manifest.json` (mode/session/hash/footer flags)

Manual fallback (secondary only):
- `./bridge_chat.sh tail --session <session_id> --lines 120`
- `rg` on `logs/bridge.jsonl` and `logs/chat.jsonl`

Migration note (honest limitation):
- For older sessions without `MODE`/`CONTRACT_PATH`/`BUNDLE_SHA256`, you can prove GPT received payload.
- You cannot prove Taylor QA mode was used for those older sessions.
- Appends raw GPT response JSON for verification

Team-first routing:

- Default team post:

```bash
./bridge_chat.sh chat "I think we should revisit this plan"
```

- Mention routing (still visible to whole team, legacy/advanced in Codex UI):

```bash
./bridge_chat.sh chat "@gpt review this plan and suggest 3 actions"
./bridge_chat.sh chat "@codex can you sanity-check this?"
./bridge_chat.sh chat "@taylor can you sanity-check this?"
```

`@gpt` causes GPT relay in the same active session.  
`@codex` triggers explicit Codex acknowledgment in timeline.  
Other mentions are team-visible intent tags.

Recommended in Codex UI: tilde commands (`~...`)

```bash
./bridge_chat.sh chat "~help"
./bridge_chat.sh chat "~options"
./bridge_chat.sh chat "~session Let's plan the rollout"
./bridge_chat.sh chat "~gpt review this diff"
./bridge_chat.sh chat "~sync"
./bridge_chat.sh chat "~codex sanity-check this plan"
./bridge_chat.sh chat "~cj please review this"
./bridge_chat.sh chat "~taylor please review this"
./bridge_chat.sh chat "~end"
./bridge_chat.sh chat "~recover"
```

Quote-safe invocation (no shell escaping issues):

```bash
printf "%s" "~gpt it's working?" | ./bridge_chat.sh chat --stdin
printf "%s" "~session Let's plan next sprint" | ./bridge_chat.sh chat --stdin
```

`chat` also auto-reads piped stdin when message arg is omitted:

```bash
printf "%s" "~gpt it's working?" | ./bridge_chat.sh chat
```

Add non-GPT messages (for agents/humans):

```bash
./bridge_chat.sh post --from taylor "I am online"
./bridge_chat.sh post --from cj "Let's plan next step"
```

Use separate sessions when needed:

```bash
./bridge_chat.sh send --session sprint-a "status check"
./bridge_chat.sh tail --session sprint-a --lines 40
```

End a session and persist/sync memory:

```bash
./bridge_chat.sh end --session sprint-a
```

Start/switch session with kickoff prompt (ends previous session first):

```bash
./bridge_chat.sh chat "/session Let's plan the onboarding feature rollout"
```

`end` behavior:

- Extracts remember-worthy items from that session
- Stores them in `logs/memory_store.jsonl`
- Sends them to GPT in a dedicated message that includes:
  - `Important BitPod App data: Update your memory`
  - `Memory pointer: memory://bitpod-app/memory_store.jsonl` (override with `--memory-pointer`)
- Stops bridge after finalize (use `--no-stop-bridge` to keep it running)

Recover stale sessions after timeout/crash:

```bash
./bridge_chat.sh recover
```

Recovery behavior:

- Scans sessions in `logs/chat.jsonl`
- Finds sessions with new message transcript content but no matching `session_finalize` marker
- Finalizes those sessions (extract + persist + optional GPT sync)
- Writes idempotent finalize markers so repeated recover runs do not duplicate work

Legacy slash commands:

```bash
./bridge_chat.sh chat "/help"
./bridge_chat.sh chat "/options"
./bridge_chat.sh chat "/team hello team"
./bridge_chat.sh chat "/gpt review this diff"
./bridge_chat.sh chat "/ask review this diff"
./bridge_chat.sh chat "/codex review this plan"
./bridge_chat.sh chat "/session Let's plan the onboarding feature rollout"
./bridge_chat.sh chat "/end"
./bridge_chat.sh chat "/recover"
```

Read recent timeline:

```bash
./bridge_chat.sh tail --lines 40
```

Follow live updates:

```bash
./bridge_chat.sh tail --follow
```

Bridge lifecycle controls:

```bash
./bridge_ctl.sh status
./bridge_ctl.sh start --session sprint-a
./bridge_ctl.sh stop --session sprint-a
```

`stop` posts `GPT Bridge left the chat` into the shared chat timeline.

Optional env vars for wrapper:

- `GPT_BRIDGE_URL` (default `http://127.0.0.1:8787/ask`)
- `GPT_BRIDGE_TOKEN` (bearer token)
- `GPT_BRIDGE_SHARED_SECRET` (fallback header)

## MCP server (2.A)

Run MCP stdio server:

```bash
python3 gpt_bridge_mcp.py
```

Exposed tool:

- `gpt_bridge_ask`
  - Forwards to bridge `POST /ask` via `GPT_BRIDGE_URL`
  - Input fields: `task_type`, `message`, `context`, `constraints`, `meta`
  - Output: JSON text of the `GPTResponse`

Required env for MCP calls:

- `GPT_BRIDGE_URL` (default `http://127.0.0.1:8787/ask`)
- `GPT_BRIDGE_TOKEN` and/or `GPT_BRIDGE_SHARED_SECRET`
- `GPT_BRIDGE_TIMEOUT_SECONDS` (optional, default `20`)

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

## One-command quick test

Run this from `gpt_bridge/`:

```bash
./quick_test.sh
```

What it does:

- Loads `.env`
- Starts bridge
- Starts a fresh `~session ...`
- Sends `~gpt reply with exactly: pong`
- Ends session
- Prints `QUICK TEST: PASS` or `QUICK TEST: FAIL`

If you send GPT messages from Terminal and want to pull GPT replies into Codex chat view:

```bash
./bridge_chat.sh chat "~sync"
```

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

## Codex MCP registration + smoke test (2.B)

1. Start HTTP bridge:

```bash
cd /Users/cjarguello/bitpod-app/tools/gpt_bridge
python3 gpt_bridge.py
```

2. Register MCP server in Codex config (`~/.codex/config.toml`):

```toml
[mcp_servers.gpt_bridge]
command = "python3"
args = ["/Users/cjarguello/bitpod-app/tools/gpt_bridge/gpt_bridge_mcp.py"]

[mcp_servers.gpt_bridge.env]
GPT_BRIDGE_URL = "http://127.0.0.1:8787/ask"
GPT_BRIDGE_TOKEN = "replace_with_long_random_token"
# GPT_BRIDGE_SHARED_SECRET = "replace_with_long_random_secret"
```

3. Restart Codex so it reconnects MCP servers.

4. Smoke test from Codex MCP tools:

- Call `gpt_bridge_ask` with:

```json
{
  "task_type": "general",
  "message": "ping",
  "constraints": {"json_only": true, "max_tokens": 300},
  "meta": {"repo": "bitpod"}
}
```

- Expected: tool returns JSON text containing `status`, `answer`, and `trace`.
- Auth failure: confirm missing/invalid token returns `isError: true` with unauthorized detail.
