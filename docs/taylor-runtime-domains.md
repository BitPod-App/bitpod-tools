# Taylor Runtime Domains

## Purpose

Define the canonical runtime path and operational expectations for Taylor in the current BitPod workspace.

## Canonical Runtime Path

- Canonical: `/Users/cjarguello/bitpod-app/bitpod-taylor-runtime`

## Runtime Modes

1. Continuous runtime

```bash
cd /Users/cjarguello/bitpod-app/bitpod-taylor-runtime
set -a; source .env; set +a
PYTHONPATH=src python3 -m taylor
```

2. One-shot health check

```bash
cd /Users/cjarguello/bitpod-app/bitpod-taylor-runtime
set -a; source .env; set +a
PYTHONPATH=src python3 -m taylor --once
```

## Current Chat Backend

- Current production backend is Zulip.
- Discord is the first post-Zulip proof-of-concept target, but transport portability remains required.
- Migration/transport contract is tracked in [BIT-37 — Migrate team session chat commands from Zulip to chosen platform](https://linear.app/bitpod-app/issue/BIT-37/migrate-team-session-chat-commands-from-zulip-to-chosen-platform).

## Required Environment

- `ZULIP_SITE`
- `ZULIP_EMAIL`
- `ZULIP_API_KEY`
- Any model/provider credentials required by runtime config.

## Credential/API Smoke Test

```bash
cd /Users/cjarguello/bitpod-app/bitpod-taylor-runtime
set -a; source .env; set +a
python3 - <<'PY'
import os, base64, json, urllib.request
site = os.environ["ZULIP_SITE"].rstrip("/")
email = os.environ["ZULIP_EMAIL"]
key = os.environ["ZULIP_API_KEY"]
auth = "Basic " + base64.b64encode(f"{email}:{key}".encode()).decode()
req = urllib.request.Request(site + "/api/v1/users/me", headers={"Authorization": auth})
print(json.loads(urllib.request.urlopen(req, timeout=20).read()).get("result"))
PY
```

## Historical Note

- Older migration-era docs may mention `/Users/cjarguello/bitpod-app/taylor-runtime`.
- Treat that path as retired historical context, not as an active compatibility target.
