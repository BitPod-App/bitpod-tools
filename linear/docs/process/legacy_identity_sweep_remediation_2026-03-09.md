# Legacy Identity Scan Report

- UTC: 2026-03-10 03:31:29Z
- Scope root: `/Users/cjarguello/bitpod-app`
- Repos: bitpod bitpod-assets bitpod-docs bitpod-taylor-runtime bitpod-tools bitregime-core sector-feeds

## Counts

| Pattern | Match count |
|---|---:|
| `bitipod\.com` | 4 |
| `@bitipod\.com` | 1 |
| `\bbitipod\b` | 6 |

## Hits (first 20 per pattern)

### bitipod\.com
- /Users/cjarguello/bitpod-app/bitpod/docs/runbooks/identity_org_domain_parity_runbook.md:89:- Legacy `bitipod.com` paths remain redirect-only where needed.
- /Users/cjarguello/bitpod-app/bitpod/docs/runbooks/identity_org_domain_parity_runbook.md:199:- [ ] Legacy `@bitipod.com` forwarding strategy documented (temporary).
- /Users/cjarguello/bitpod-app/bitpod-tools/linear/docs/process/domain_email_policy_bitpod_app_v1_2026-03-07.md:10:3. Legacy `bitipod.com` forwarding may remain temporarily during migration, but no new account creation should use legacy domain.
- /Users/cjarguello/bitpod-app/bitpod-tools/linear/docs/process/domain_email_policy_bitpod_app_v1_2026-03-07.md:30:Disable legacy `bitipod.com` forwarding only when all are true:

### @bitipod\.com
- /Users/cjarguello/bitpod-app/bitpod/docs/runbooks/identity_org_domain_parity_runbook.md:199:- [ ] Legacy `@bitipod.com` forwarding strategy documented (temporary).

### \bbitipod\b
- /Users/cjarguello/bitpod-app/bitpod/docs/runbooks/identity_org_domain_parity_runbook.md:25:- Active code/config scan shows no remaining `bitipod` references in core repos when excluding logs/artifacts.
- /Users/cjarguello/bitpod-app/bitpod/docs/runbooks/identity_org_domain_parity_runbook.md:89:- Legacy `bitipod.com` paths remain redirect-only where needed.
- /Users/cjarguello/bitpod-app/bitpod/docs/runbooks/identity_org_domain_parity_runbook.md:199:- [ ] Legacy `@bitipod.com` forwarding strategy documented (temporary).
- /Users/cjarguello/bitpod-app/bitpod/docs/runbooks/identity_org_domain_parity_runbook.md:211:- `rg -n -i "bitipod\\.com|@bitipod\\.com|\\bbitipod\\b" ...` scan output attached
- /Users/cjarguello/bitpod-app/bitpod-tools/linear/docs/process/domain_email_policy_bitpod_app_v1_2026-03-07.md:10:3. Legacy `bitipod.com` forwarding may remain temporarily during migration, but no new account creation should use legacy domain.
- /Users/cjarguello/bitpod-app/bitpod-tools/linear/docs/process/domain_email_policy_bitpod_app_v1_2026-03-07.md:30:Disable legacy `bitipod.com` forwarding only when all are true:

## Classification Guidance

- Runtime/config references should be remediated.
- Historical evidence docs may retain legacy references when clearly annotated.

## Remediation Disposition (2026-03-10)

- Verified: zero legacy-domain hits in active runtime/config code paths across scanned repos.
- Remaining matches are documentation references that intentionally describe legacy forwarding or historical migration context.
- Exception set (intentional for now):
  - `/Users/cjarguello/bitpod-app/bitpod/docs/runbooks/identity_org_domain_parity_runbook.md`
  - `/Users/cjarguello/bitpod-app/bitpod-tools/linear/docs/process/domain_email_policy_bitpod_app_v1_2026-03-07.md`
- Action: keep as documented legacy exceptions; revisit when legacy forwarding is fully retired in Phase 3 hardening.
