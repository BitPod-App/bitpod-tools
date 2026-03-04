# BIT-44: Linear x GitHub Sync MVP

Status: MVP baseline (safe, low-risk, documentation-first)

## 1) Canonical formats

### 1.1 GitHub PR title
- Required: start with Linear key in brackets.
- Format: `[BIT-123] Short title`
- Length policy:
  - Recommended: 72-88 chars total
  - Soft max: 100 chars
  - Hard max: 120 chars

Notes:
- `PR #...` is NOT part of GitHub PR title policy.
- Linear linking trigger is the `BIT-123` reference, not `PR #`.

### 1.2 Codex chat PR mention format
- Base format:
  - `[PR #123 — short-title…](https://github.com/<org>/<repo>/pull/123)`
- If mention comes from a PR comment link, append comment suffix:
  - `[PR #123 — short-title… -comment_456789](https://github.com/<org>/<repo>/pull/123#issuecomment-456789)`
- Truncation rule for `short-title` in chat:
  - 28 chars max, then `…`

### 1.3 Codex chat Linear comment link format
- Base format:
  - `[BIT-123 — short-title… -comment_<id>](https://linear.app/<workspace>/issue/BIT-123/<slug>#comment-<id>)`
- Truncation rule for `short-title` in chat:
  - 28 chars max, then `…`

## 2) Expected integration behavior (MVP assumptions)

- One valid Linear reference (`BIT-123`) in PR title/description is usually enough to link PR<->Linear issue.
- Once linked, PR state transitions can update Linear issue status IF team workflow automation is configured.
- Full bidirectional comment mirroring is NOT assumed as default behavior.

## 3) Smoke test checklist

1. Create/update Linear issue `BIT-xxx` in target team.
2. Open PR with title `[BIT-xxx] ...`.
3. Confirm PR appears in Linear issue attachments/activity.
4. Move PR states (draft -> open -> review request -> merge) and observe Linear status transitions.
5. Post one explicit manual cross-link comment in both systems:
   - Linear comment includes PR link.
   - PR comment includes Linear issue link.
6. Record observed behavior in BIT-44 comments.

## 4) Definition of done for MVP

- Canonical formatting rules documented in repo.
- PR linkage pattern standardized (`[BIT-xxx]` in title).
- Evidence captured for whether status automation is active.
- Known gaps captured as phase-2 backlog.

## 5) Phase-2 TODO backlog (not in MVP)

- Auto-mirror selected comments between Linear and GitHub with guardrails.
- Trigger rules for when copy-pasted links should create cross-posts.
- Multi-issue PR policy (`[BIT-123][BIT-124]` vs primary+secondary model).
- Enforcement checks (CI/lint) for PR title and reference formatting.
