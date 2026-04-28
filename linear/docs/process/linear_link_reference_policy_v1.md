# Linear Link Reference Policy v1

Status: Active
Owner: Product Development
Related: BIT-43, BIT-33
Last updated: 2026-04-28

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

## PR-to-Linear closeout comment formats

Use these formats for merge closeout, retroactive linking, and Linear normalization work.

GitHub PR comment body:

```md
Retroactively linked Linear issues:
- [BIT-000 — Full Issue Title](https://linear.app/bitpod-app/issue/BIT-000/issue-slug)
```

Linear issue comment body:

```md
Retroactively linked to GitHub PR: [BitPod-App/repo-name PR #123 — PR Title](https://github.com/BitPod-App/repo-name/pull/123).
```

Rules:

- Use one clean comment per PR and one clean comment per issue for the link-back record.
- Update an existing retroactive-link comment instead of adding duplicates.
- Include all mapped Linear issues in the PR comment when a PR closes multiple issues.
- Attach the GitHub PR link to the Linear issue when tooling supports attachments/links.
- If the PR title is unavailable, use the canonical PR fallback format rather than a bare URL.

## Guardrails

- Do not output bare `BIT-000` IDs without a link unless explicitly requested.
- Do not output bare `#123` PR references without a link unless explicitly requested.
- Do not leave shorthand-only retroactive linking comments when the issue title and URL are available.
- If verification certainty is low, mark the reference as inferred/degraded instead of guessing the title.

## Verification checklist

- Confirm all new references in comments/docs follow canonical or degraded fallback format.
- Confirm fallback still includes full URL.
- Confirm policy is linked from the operating guide.
