# Canonical Domain/Email Policy v1 (`bitpod.app`)

Related issue: https://linear.app/bitpod-app/issue/BIT-18/canonicalize-domainemail-policy-bitpodapp-email-auth-checklist
Date: 2026-03-07

## Canonical policy

1. Canonical domain for product/integrations: `bitpod.app` only.
2. New external accounts/integrations must use `@bitpod.app` identity where possible.
3. Legacy `bitipod.com` forwarding may remain temporarily during migration, but no new account creation should use legacy domain.
4. Decommission legacy forwarding only after cutover trigger criteria are met.

## DNS / email auth checklist (current)

| Control | Status | Evidence |
|---|---|---|
| Root SPF TXT present | PASS | `v=spf1 include:_spf.mx.cloudflare.net ~all` |
| DMARC TXT present | PASS (monitor mode) | `v=DMARC1; p=none; ...` |
| MX configured for Cloudflare Email Routing | PASS | `route1/2/3.mx.cloudflare.net` |
| DKIM TXT verified | PENDING | common selectors checked with no TXT response |
| DMARC enforcement level | PENDING HARDENING | currently `p=none` (monitor-only) |

## Web/domain checks

- `https://bitpod.app` resolves and serves through Cloudflare (HTTP 404 with noindex from app/service)\
- `https://www.bitpod.app` redirects to apex (`301`)

## Legacy forwarding retirement trigger

Disable legacy `bitipod.com` forwarding only when all are true:

1. All active integrations/accounts have been updated to `@bitpod.app`.
2. DKIM is configured and verified for sending provider(s).
3. DMARC moved from `p=none` to enforced mode (`quarantine` or `reject`) with monitoring period complete.
4. Two-week observation window shows no delivery/auth regressions.

## Immediate next actions

1. Add/verify DKIM selector records for active sender(s) in Cloudflare/email provider.
2. Keep DMARC in monitor mode briefly, review aggregate reports, then harden to enforcement.
3. Document exact sender inventory (transactional, support, alerts, bots) to avoid partial auth setup.

## Commands used for verification

```bash
dig +short bitpod.app A
dig +short bitpod.app AAAA
dig +short www.bitpod.app CNAME
dig +short bitpod.app TXT
dig +short _dmarc.bitpod.app TXT
dig +short bitpod.app MX
curl -sSI https://bitpod.app
curl -sSI https://www.bitpod.app
```
