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

For active repos, CODEOWNERS should route by default to the default Vera QA reviewer lane.

```text
# BitPod baseline CODEOWNERS (V1.5)
* @BitPod-App/veraqa-tier-1
```

No other reviewer team should be in required-code-owner routing by default.

### Branch protection / rulesets baseline

- Use fixed GitHub branch policy for merge safety (`required_approving_review_count: 1` as current safety baseline).
- Do not encode a fixed maintainer-only required-reviewer team in rulesets or branch protection.
- Branch/ruleset required review teams should reflect this policy text and map to the live VeraQA tiering policy instead of static maintainer-gating.

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

- These are T2-heavy repos, but should **not** force T2 for tiny follow-up PRs.
- Start as T2 unless all of the **T2-small-exemption** conditions are true:
  - `files_changed <= 3`
  - `lines_changed <= 120`
  - `R < 4`
  - no critical-path paths touched

- If all conditions are true, route as **T1**.
- Otherwise route as **T2**.

### 3) T3 cadence (dynamic, not time-fixed)

For each high-impact repo (`sector-feeds`, `bitregime-core`) use daily dynamic sampling:

- Let `N` = number of PRs that completed merge flow in the calendar day in that repo.
- Let `L` = number of those PRs where `R >= 7` (large/high-risk PRs).
- Required T3 quota for the day:

```text
required_t3 = max(1, ceil(N / 4)) + L
```

<!--
## Commented out short description (human readable)

- `N` is the number of PRs that reached merge-complete flow in that repo for the calendar day.
- `L` is how many of those PRs had `R >= 7` (high-risk/big PRs).
- If `N=0`, no T3 requirement for that repo/day.
- If there is any activity (`N>0`), at least one T3 is required (`max(1, ceil(N/4))`).
- High-risk PRs add one extra mandatory T3 each (`+L`).
- Example: `N=5`, `L=1` => `max(1, ceil(5/4)) + 1 = 3`
  (2 routine-cycle T3s + 1 high-risk-required T3).
-->

- This means:
  - at least one periodic T3 when there is activity,
  - extra T3 for large/high-risk PRs.
- If no PRs in the day, no T3 quota is required.
- T3 queue must be satisfied before merge-closeout for day-end handoff.

### 4) Cost discipline and overuse controls

- T2 and T3 are explicit escalations, not defaults.
- Small follow-up PRs in high-impact repos are intentionally kept on T1 when they are low-risk.
- T3 is periodic and sampling-based so only a subset of important work gets expensive deep review.

## Team/ruleset implementation notes

When implementing in GitHub:

1. keep maintainer teams out of the reviewer-routing default path;
2. ensure `veraqa-tier-1` is the CODEOWNERS routing default;
3. keep required review counts aligned with this model;
4. add lightweight policy-driven reviewer escalation outside static rulesets for T2/T3, plus periodic sampling jobs / triage review packets.

## Recommended next actions

1. Move maintainer gating references (`core-maintainers` / `code-maintainers`) out of reviewer-routing defaults.
2. Keep maintainer teams as write-only maintainers.
3. Set/keep VeraQA tier teams as the authoritative reviewer routing source.
4. Implement the PR-score + daily T3 quota process in CI or merge-prep tooling.
5. Document per-repo exceptions and keep a small explicit override log for trust auditability.

## Out of scope

- Changing non-review access roles without a dedicated access review.
- Replacing repo-level ownership decisions.
- Full merge-policy decisions that still rely on explicit CJ acceptance paths for exception handling.
