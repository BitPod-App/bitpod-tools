# Linear Link Reference Policy v1

Status: Active
Owner: Product Development
Related: [BIT-43 — Enforce BIT link format policy (BIT-000 + full Linear title hyperlink) with rollout guardrails](https://linear.app/bitpod-app/issue/BIT-43/enforce-bit-link-format-policy-bit-000-full-linear-title-hyperlink), [BIT-33 — Implement capability-state + truth-label incident protocol for all migration execution](https://linear.app/bitpod-app/issue/BIT-33/implement-capability-state-truth-label-incident-protocol-for-all)
Last updated: 2026-06-03

## Purpose

Standardize how Linear issue references and GitHub PR references are emitted in chat, docs, and automation comments.

## Canonical Linear issue format

Use this whenever issue title is available:

`[BIT-000 — Full Issue Title](https://linear.app/bitpod-app/issue/BIT-000/issue-slug)`

## Degraded fallback format

If title lookup is unavailable but the Linear URL is known, keep the reference
clickable and note degraded formatting:

`[BIT-000 — title unavailable](https://linear.app/bitpod-app/issue/BIT-000/issue-slug) (degraded: title lookup unavailable)`

If neither title nor URL can be verified, do not fabricate either one:

`BIT-000 (degraded: Linear title and URL unavailable)`

That last form is allowed only as a temporary capability fallback for the
current message, log, or automation run. It must not be treated as canonical
policy output once title or URL lookup is restored.

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

- Prefer canonical Linear issue links for newly introduced references:
  `[BIT-000 — Full Issue Title](https://linear.app/bitpod-app/issue/BIT-000/issue-slug)`.
- Do not output bare `BIT-000` IDs without a link unless explicitly requested.
- Do not output bare `#123` PR references without a link unless explicitly requested.
- Do not leave shorthand-only retroactive linking comments when the issue title and URL are available.
- If verification certainty is low, mark the reference as inferred/degraded instead of guessing the title.

## Rollout guardrails

- Roll this policy out as normalization first, not as a broad hard-fail gate.
- A missing title lookup should degrade the one reference, not fail the whole
  report, PR body, Linear comment, or automation run.
- Do not silently guess issue titles, PR titles, or slugs to satisfy the format.
- Do not retroactively rewrite old comments or docs solely to eliminate bare
  IDs unless the owning workflow explicitly asks for normalization.
- When adding checks, start with warning/report-only behavior unless the checked
  surface has opted into hard enforcement and has a verified lookup path.
- If a tool can fetch a title but the fetch fails, emit the degraded fallback
  and include the failure in the run evidence when the surface already reports
  evidence or blockers.

## Verification checklist

- Confirm all new references in comments/docs follow canonical or degraded fallback format.
- Confirm fallback stays clickable when the Linear URL is available.
- Confirm no title or slug is fabricated to satisfy the canonical format.
- Confirm policy is linked from the operating guide.
