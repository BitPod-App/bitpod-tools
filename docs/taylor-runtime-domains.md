# Taylor Runtime Domains (Legacy + New)

## Purpose

Define canonical runtime paths and operational expectations for Taylor across old and new BitPod layouts.

## Canonical Runtime Path

- Preferred: `/Users/cjarguello/bitpod-app/taylor-runtime`
- Legacy compatibility path (if still present): `/Users/cjarguello/bitpod-app/bitpod-taylor-runtime`

## Runtime Modes

1. Continuous runtime

```bash
cd /Users/cjarguello/bitpod-app/taylor-runtime
set -a; source .env; set +a
PYTHONPATH=src python3 -m taylor
```

2. One-shot health check

```bash
cd /Users/cjarguello/bitpod-app/taylor-runtime
set -a; source .env; set +a
PYTHONPATH=src python3 -m taylor --once
```

## Current Chat Backend

- Current production backend is Zulip.
- Discord migration is tracked separately in `BIT-37`.

## Required Environment

- `ZULIP_SITE`
- `ZULIP_EMAIL`
- `ZULIP_API_KEY`
- Any model/provider credentials required by runtime config.

## Credential/API Smoke Test

```bash
cd /Users/cjarguello/bitpod-app/taylor-runtime
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

## Migration Notes

- New docs and scripts should target `taylor-runtime` path.
- Keep compatibility notes for `bitpod-taylor-runtime` only until fully retired.
