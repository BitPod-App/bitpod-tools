# GitHub Team Purpose, Reviewer Routing, and Vera QA Tier Policy v2

## Purpose

Define the current BitPod review-routing model and the dynamic VeraQA tier policy that can be used by both team workflows and ruleset governance.

This v2 policy replaces the prior maintainer-gating model for review UX and required-reviewer routing.

## Scope

Applies to active repos in org `BitPod-App` for PR review routing and merge-governance controls.

## Team purpose model (review routing)

### Maintainer teams (`core-maintainers`, `code-maintainers` where present)

- **Purpose now:** repository stewardship and write-oriented operating authority.
- **Routing role:** *not* used for default reviewer-gating.
- **Constraint:** do not include in CODEOWNERS review-routing defaults, branch-reviewer-only gate targets, or rulesets as sole required review source.

### Vera QA teams (review routing)

#### `veraqa-tier-1` (aka `VeraQA-T1`)
- Team membership policy: currently only `vera-qa` is expected in each VeraQA team unless CJ approves adding others.
- Default reviewer lane for most repos.
- Targets routine PR quality checks with a low-cost model.

#### `veraqa-tier-2` (aka `VeraQA-T2`)
- Team membership policy: currently only `vera-qa` is expected in each VeraQA team unless CJ approves adding others.
- Elevated review lane for high-risk or large PRs.
- Uses `Codex-3.0` high-reasoning execution.

#### `veraqa-tier-3-audit` (aka `VeraQA-T3`)
- Team membership policy: currently only `vera-qa` is expected in each VeraQA team unless CJ approves adding others.
- Optional periodic deep-review lane, fed by OpenAI Native Code Review.
- Uses external, high-signal review only when policy says it is needed.
- Keeps occasional deep assurance without forcing every PR into expensive deep review.

## Target reviewer-routing baseline

### Repo CODEOWNERS baseline

CODEOWNERS should route by default to the appropriate Vera QA reviewer lane.

Default/high-impact split:

```text
# Default active repos
* @BitPod-App/veraqa-tier-1

# High-impact repos: sector-feeds, bitregime-core
* @BitPod-App/veraqa-tier-2
```

No maintainer team should be in default QA review routing.

## GitHub permission note

GitHub only treats a team as a valid CODEOWNERS owner when that team has write access to the repository. For VeraQA teams, write access is a GitHub routing requirement, not implementation ownership. The role boundary remains QA review only.

### Branch protection / rulesets baseline

- Use lightweight GitHub branch policy for merge safety (`required_approving_review_count: 1` as current safety baseline).
- Keep `require_code_owner_reviews=false` so CODEOWNERS guides reviewer routing without creating hard-to-bypass governance friction.
- Do not encode maintainer teams as required reviewer gates in rulesets or branch protection.

## Dynamic Vera QA tier policy (recommended)

This allows us to keep high assurance without overusing T2/T3.

### 1) PR risk score (R)

Compute a lightweight score per PR:

- `+3` for each risk label in `risk:high`, `risk:security`, `migration`, `data`, `secrets`, `production`, `release`
- `+2` if `files_changed >= 8`
- `+2` if `lines_changed >= 500`
- `+2` if any path touches critical scope:
  - `/.github/`, `.github/workflows/`, `migrations/`, `scripts/`, `deploy/`, `infra/`, `runtime/`, `cloudflare/`, `terraform/`
- `+1` if PR is marked as `blocking` by PM queue discipline

Interpretation:
- `R >= 4` -> **T2 required**
- `R >= 7` -> **T2 + T3 required**

### 2) Repo tier map

#### Default repos (all active repos except listed below)
- Start as **T1**.
- Upgrade to **T2** if `R >= 4`.

#### Team-scoped high-impact repos
`sector-feeds`, `bitregime-core`

- Default to **T2**.
- Keep these repos on T2 even for small follow-up PRs because their blast radius and operating importance are higher.
- Escalate to **T3** only for exceptional risk, periodic deep audit, or explicit Taylor/CJ request.

### 3) T3 usage

T3 is a rare deep-audit lane, not normal merge gating.

Use T3 only when one of these is true:

- explicit Taylor/CJ request,
- exceptional risk or high blast radius,
- periodic sample chosen for assurance.

There is no fixed daily quota in this guidance. Add automation later only if review misses or bypasses become frequent enough to justify it.

### 4) Cost discipline and overuse controls

- T2 is the default for `sector-feeds` and `bitregime-core`; in other repos it is an escalation.
- T3 is rare and should not be used as routine merge gating.
- Keep the model understandable before adding automation or stricter rules.

## Team/ruleset implementation notes

When implementing in GitHub:

1. keep maintainer teams out of the reviewer-routing default path;
2. use `veraqa-tier-1` as the default CODEOWNERS route for ordinary repos;
3. use `veraqa-tier-2` as the default CODEOWNERS route for `sector-feeds` and `bitregime-core`;
4. keep required review counts lightweight and use CODEOWNERS as routing guidance rather than a hard-to-bypass gate;
5. use T3 only for exceptional risk, periodic deep audit, or explicit Taylor/CJ request.


## PR readiness and draft policy

Default to a normal pull request when the change is intended to be review-ready.

Use a draft pull request only when the work is genuinely incomplete, exploratory, waiting on required validation, or intentionally opened as an early checkpoint. The PR body should state what is missing before it can be marked ready for review.

Do not use draft status as a default safety habit for finished work. If validation has run and the author believes the change is ready for review, open a normal PR.

## Recommended next actions

1. Move maintainer gating references (`core-maintainers` / `code-maintainers`) out of reviewer-routing defaults.
2. Keep maintainer teams as write-only maintainers.
3. Set/keep VeraQA tier teams as the reviewer routing source.
4. Keep bypass guidance lightweight: admins may bypass when needed and should leave a short visible reason when QA is skipped.
5. Revisit stricter automation only if bypasses or routing misses become frequent.

## Out of scope

- Changing non-review access roles without a dedicated access review.
- Replacing repo-level ownership decisions.
- Full merge-policy decisions that still rely on explicit CJ acceptance paths for exception handling.
