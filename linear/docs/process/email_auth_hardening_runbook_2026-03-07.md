# Email Auth Hardening Runbook (BIT-54)

Related issue: https://linear.app/bitpod-app/issue/BIT-54/email-auth-hardening-verify-dkim-selectors-and-enforce-dmarc-policy
Date: 2026-03-07
Domain: `bitpod.app`

## Current known state

- SPF at apex present: `v=spf1 include:_spf.mx.cloudflare.net ~all`
- DMARC present: `p=none` (monitor mode)
- MX present (Cloudflare Email Routing)
- DKIM selectors not yet verified for active sender providers
- Cloudflare API token currently available to automation has `zone:read` but not `dns_records:read` (cannot programmatically list selectors yet)

## 2026-03-07 live evidence snapshot

Verified via terminal:

```bash
dig +short bitpod.app TXT
dig +short _dmarc.bitpod.app TXT
```

Observed:
- `openai-domain-verification=dv-E8xAQo7JvLQb23GlwUrcKAFd`
- `v=spf1 include:_spf.mx.cloudflare.net ~all`
- `v=DMARC1; p=none; rua=mailto:cj.project.hq@gmail.com; fo=1; adkim=s; aspf=s; pct=100`

Cloudflare API permission probe:

```bash
curl /zones?name=bitpod.app      # success
curl /zones/<id>/dns_records     # authentication error (missing dns read scope)
```

Implication:
- We can confirm public SPF/DMARC posture now.
- We cannot enumerate authoritative DKIM selector records until token scopes are expanded or selectors are provided from sender dashboards.

## Goal state

1. DKIM verified for all active sender providers
2. DMARC moved from monitor (`p=none`) to enforcement (`quarantine` then `reject`)
3. No delivery regressions during/after enforcement

## Execution plan

### Step 1 — Sender inventory

Build explicit sender list:
- transactional sender(s)
- support mailbox platform
- alerting/bot sender(s)
- marketing/newsletter sender(s)

Output:
- provider -> required DKIM selector records table

### Step 2 — DKIM record deployment

For each provider, add required TXT records in Cloudflare DNS:
- `<selector>._domainkey.bitpod.app TXT <provider-public-key>`

Verify each selector:
```bash
dig +short <selector>._domainkey.bitpod.app TXT
```

### Step 3 — DMARC monitor period

Keep DMARC at `p=none` while collecting aggregate reports (`rua`).

Check for:
- unauthorized sources
- alignment failures (SPF/DKIM)

### Step 4 — DMARC enforcement rollout

Progressive rollout:
1. `p=quarantine; pct=25`
2. `p=quarantine; pct=100`
3. `p=reject; pct=100`

Rollback: revert to prior DMARC value if mail rejection spikes.

### Step 5 — Post-change validation

- Send test mail from each provider to external inboxes.
- Confirm SPF/DKIM/DMARC alignment passes.
- Record evidence links and timestamps.

## Evidence checklist

- Sender inventory table
- DKIM selector verification outputs
- DMARC TXT before/after snapshots
- Delivery test results
- Final policy state (`reject`) confirmation

## Commands

```bash
dig +short bitpod.app TXT
dig +short _dmarc.bitpod.app TXT
dig +short bitpod.app MX
# per selector
dig +short <selector>._domainkey.bitpod.app TXT

# reusable probe helper (writes markdown report)
linear/scripts/email_auth_probe.sh bitpod.app
```
