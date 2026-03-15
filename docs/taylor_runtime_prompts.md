# Taylor Runtime Prompts (Run + Test)

## Runtime Path
- `/Users/cjarguello/bitpod-app/bitpod-taylor-runtime`
- Legacy compatibility path: `/Users/cjarguello/bitpod-app/taylor-runtime`

## Start
```bash
cd /Users/cjarguello/bitpod-app/bitpod-taylor-runtime
set -a; source .env; set +a
PYTHONPATH=src python3 -m taylor
```

## One-Shot Check
```bash
cd /Users/cjarguello/bitpod-app/bitpod-taylor-runtime
set -a; source .env; set +a
PYTHONPATH=src python3 -m taylor --once
```

## Zulip Prompts (in channel/topic)
- `@Taylor help`
- `@Taylor status`
- `@Taylor summarize`
- `@Taylor close only`
- `@Taylor change this to review`

## Credential/API Verification
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

## Common Failures
- `Missing required env vars`: `.env` not loaded in shell.
- DNS/network errors: runtime can’t reach Zulip domain.
- No replies in Zulip: runtime process not running or bot not subscribed to stream/topic.
