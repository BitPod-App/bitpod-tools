# DKIM Public Selector Scan (2026-03-08)

Related issue: https://linear.app/bitpod-app/issue/BIT-54/email-auth-hardening-verify-dkim-selectors-and-enforce-dmarc-policy

## Method

Public DNS brute scan of common selector names (no Cloudflare API required):

- domain: `bitpod.app`
- pattern: `<selector>._domainkey.bitpod.app TXT`
- selectors tested:
  - default, selector1, selector2, s1, s2, k1, k2,
  - google, zoho, mandrill, mg, m1, m2,
  - sendgrid, mailjet, postmark, pm, amazonses, brevo,
  - sparkpost, protonmail, smtp, dkim

Raw output file:
- `/tmp/bit54_dkim_selector_scan_2026-03-08.txt`

## Result

- No tested selectors resolved (`NONE` for all tested names).

## Interpretation

- No public DKIM selectors were found among common/default names.
- This does **not** prove DKIM absence universally (custom selectors may exist).
- Authoritative selector inventory still requires either:
  1) Cloudflare DNS-record-read token scope, or
  2) provider dashboards that disclose exact selector names.
