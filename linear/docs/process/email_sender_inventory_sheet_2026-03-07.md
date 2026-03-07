# Email Sender Inventory Sheet (BIT-54)

Date: 2026-03-07
Domain: `bitpod.app`

## Verified DNS baseline

- SPF: `v=spf1 include:_spf.mx.cloudflare.net ~all`
- DMARC: `v=DMARC1; p=none; rua=mailto:cj.project.hq@gmail.com; fo=1; adkim=s; aspf=s; pct=100`
- MX (Cloudflare Email Routing):
  - `route1.mx.cloudflare.net`
  - `route2.mx.cloudflare.net`
  - `route3.mx.cloudflare.net`

## Sender/provider inventory (fill)

| Function | Provider | From address/domain | DKIM selector(s) | DNS record added? | Verified (`dig`) | Notes |
|---|---|---|---|---|---|---|
| Transactional app email | UNKNOWN | UNKNOWN | UNKNOWN | no | no | |
| Support/helpdesk | UNKNOWN | UNKNOWN | UNKNOWN | no | no | |
| Alerts/bot notifications | UNKNOWN | UNKNOWN | UNKNOWN | no | no | |
| Marketing/newsletter | UNKNOWN | UNKNOWN | UNKNOWN | no | no | |
| Forwarding-only mailbox | Cloudflare Email Routing | `*@bitpod.app` | n/a | yes | yes | receiving only |

## Verification commands

```bash
dig +short bitpod.app TXT
dig +short _dmarc.bitpod.app TXT
dig +short bitpod.app MX
# per selector discovered from provider docs/dashboard
dig +short <selector>._domainkey.bitpod.app TXT
```

## Completion gate for BIT-54

1. All active sender providers identified.
2. DKIM selectors published and verified for each sender provider.
3. DMARC progressed from `p=none` -> `quarantine` -> `reject` with monitoring evidence.
4. Delivery tests pass after enforcement.
