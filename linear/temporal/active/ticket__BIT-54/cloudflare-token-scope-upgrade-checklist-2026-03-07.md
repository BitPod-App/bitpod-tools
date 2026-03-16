# Cloudflare Token Scope Upgrade Checklist (BIT-54)

Related issue: https://linear.app/bitpod-app/issue/BIT-54/email-auth-hardening-verify-dkim-selectors-and-enforce-dmarc-policy
Date: 2026-03-07

## Why this is needed

Current token can read zone metadata but cannot read DNS records (`/zones/<id>/dns_records` returns auth error code 10000).

## Required token scopes

Minimum for selector inventory:
- `Zone -> DNS -> Read`

If we also want automated DNS updates later:
- `Zone -> DNS -> Edit`

Resource scope:
- Limit token to zone: `bitpod.app`

## UI steps

1. Cloudflare Dashboard -> My Profile -> API Tokens -> Create Token.
2. Use "Create Custom Token".
3. Add permissions listed above.
4. Restrict zone resources to only `bitpod.app`.
5. Save and copy token once.
6. Update runtime secret destination used by BitPod deploy/probes.

## Verification commands

```bash
cd /Users/cjarguello/BitPod-App/bitpod
set -a; source .bitpod_runtime.env; set +a

# should succeed
curl -sS -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  "https://api.cloudflare.com/client/v4/zones?name=bitpod.app&status=active" | jq -c '{success,errors}'

# should succeed after scope fix
zone_id=$(curl -sS -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  "https://api.cloudflare.com/client/v4/zones?name=bitpod.app&status=active" | jq -r '.result[0].id')

curl -sS -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  "https://api.cloudflare.com/client/v4/zones/$zone_id/dns_records?per_page=5" | jq -c '{success,errors,result_count:(.result|length)}'
```

## Expected result

- Both calls return `success=true`.
- Once confirmed, rerun:

```bash
/Users/cjarguello/BitPod-App/bitpod-tools/linear/scripts/email_auth_probe.sh bitpod.app
```

and append output to BIT-54 evidence.
