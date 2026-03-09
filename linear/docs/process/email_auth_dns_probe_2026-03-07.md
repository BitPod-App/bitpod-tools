# Email Auth DNS Probe (2026-03-07)

Related issue: https://linear.app/bitpod-app/issue/BIT-54/email-auth-hardening-verify-dkim-selectors-and-enforce-dmarc-policy

## Public DNS checks

```bash
dig +short TXT bitpod.app
dig +short TXT _dmarc.bitpod.app
```

Output snapshot:

- `"openai-domain-verification=dv-E8xAQo7JvLQb23GlwUrcKAFd"`
- `"v=spf1 include:_spf.mx.cloudflare.net ~all"`
- `"v=DMARC1; p=none; rua=mailto:cj.project.hq@gmail.com; fo=1; adkim=s; aspf=s; pct=100"`

## Cloudflare API scope probe

Command path:

- `GET /client/v4/zones?name=bitpod.app` -> success
- `GET /client/v4/zones/<zone_id>/dns_records` -> `{"success":false,"errors":[{"code":10000,"message":"Authentication error"}]}`

Interpretation:

- Token has sufficient zone-read visibility.
- Token lacks DNS-record-read scope for authoritative selector enumeration.

## Next action

Rotate or create a Cloudflare API token scoped to:

- `Zone -> DNS -> Read` (minimum)
- Optional for updates: `Zone -> DNS -> Edit`

Then rerun DNS selector inventory and update BIT-54 evidence.
