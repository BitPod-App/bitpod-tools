# Linear Link Reference Policy v1

Status: Active
Owner: Product Development
Related: BIT-43, BIT-33
Last updated: 2026-03-09

## Purpose

Standardize how Linear issue references and GitHub PR references are emitted in chat, docs, and automation comments.

## Canonical Linear issue format

Use this whenever issue title is available:

`[BIT-000 — Full Issue Title](https://linear.app/bitpod-app/issue/BIT-000/issue-slug)`

## Degraded fallback format

If title lookup is unavailable, emit explicit fallback and note degraded formatting:

`BIT-000 (title unavailable) — https://linear.app/bitpod-app/issue/BIT-000/issue-slug`

## Canonical PR format

Preferred:

`[BitPod-App/repo-name PR #123 — PR Title](https://github.com/BitPod-App/repo-name/pull/123)`

Allowed shorthand:

`[PR #123 — PR Title](https://github.com/BitPod-App/repo-name/pull/123)`

Fallback:

`[BitPod-App/repo-name PR #123](https://github.com/BitPod-App/repo-name/pull/123)` (title unavailable)

## Guardrails

- Do not output bare `BIT-000` IDs without a link unless explicitly requested.
- Do not output bare `#123` PR references without a link unless explicitly requested.
- If verification certainty is low, mark the reference as inferred/degraded instead of guessing the title.

## Verification checklist

- Confirm all new references in comments/docs follow canonical or degraded fallback format.
- Confirm fallback still includes full URL.
- Confirm policy is linked from the operating guide.

