# GitHub Team Purpose, Reviewer Routing, and Vera QA Gate Policy v3

## Purpose

Define the current BitPod review-routing model and the single VeraQA gate policy that can be used by both team workflows and ruleset governance.

This v3 policy replaces the VeraQA tier-team routing model. Vera QA depth is decided by Vera/runtime/process, not by GitHub team names.

## Scope

Applies to active repos in org `BitPod-App` for PR review routing and merge-governance controls.

## Team purpose model (review routing)

### Maintainer teams (`core-maintainers`, `code-maintainers` where present)

- **Purpose now:** repository stewardship and write-oriented operating authority.
- **Routing role:** *not* used for default reviewer-gating.
- **Constraint:** do not include in CODEOWNERS review-routing defaults, branch-reviewer-only gate targets, or rulesets as sole required review source.

### Vera QA gate team (review routing)

#### `veraqa`
- Team membership policy: only verified Vera review identities belong in the VeraQA gate. The current fallback identity is `vera-qa`; BIT-595/BIT-596 decide whether a GitHub App/bot actor can replace or augment it. `taylor-01` and CJ/admin must not be VeraQA team members because Taylor01 PM acceptance and admin bypass are separate from code review.
- Default reviewer gate for active repos.
- Stable indirection layer for CODEOWNERS so the concrete Vera review actor can change without rewriting every repo.
- Does not encode QA depth. Vera/runtime/process chooses baseline, escalated, or deep-audit review depth per PR risk.

#### Superseded tier teams
- `veraqa-tier-1`, `veraqa-tier-2`, and `veraqa-tier-3-audit` are historical routing concepts only.
- Do not use tier teams as active CODEOWNERS routes.
- After all active repos/docs/open PR dependencies are migrated, remove or retire these teams from active org routing.

## Target reviewer-routing baseline

### Repo CODEOWNERS baseline

CODEOWNERS should route by default to the single VeraQA gate:

```text
* @BitPod-App/veraqa
```

No maintainer team and no VeraQA tier team should be in default QA review routing.

## GitHub permission note

GitHub only treats a team as a valid CODEOWNERS owner when that team has write access to the repository. For VeraQA teams, write access is a GitHub routing requirement, not implementation ownership. The role boundary remains QA review only.

### Branch protection / rulesets baseline

- Use a lightweight approval count (`required_approving_review_count: 1`) with a real VeraQA CODEOWNERS gate.
- Keep `require_code_owner_reviews=true` so CODEOWNERS is a real VeraQA gate, not just a hint.
- Keep `dismiss_stale_reviews=true` and `require_last_push_approval=true` so new commits after approval require fresh review and the last pusher cannot be the approving reviewer.
- Keep admin enforcement enabled so admin status does not become the routine bypass path.
- Do not encode maintainer teams as required reviewer gates in rulesets or branch protection.

## Dynamic Vera QA depth policy (recommended)

This allows us to keep high assurance without encoding T2/T3 as GitHub teams.

### 1) PR risk score (R)

Compute a lightweight score per PR:

- `+3` for each risk label in `risk:high`, `risk:security`, `migration`, `data`, `secrets`, `production`, `release`
- `+2` if `files_changed >= 8`
- `+2` if `lines_changed >= 500`
- `+2` if any path touches critical scope:
  - `/.github/`, `.github/workflows/`, `migrations/`, `scripts/`, `deploy/`, `infra/`, `runtime/`, `cloudflare/`, `terraform/`
- `+1` if PR is marked as `blocking` by PM queue discipline

Interpretation:
- `R >= 4` -> **escalated Vera review required**
- `R >= 7` -> **escalated Vera review required; consider rare deep audit only by explicit Taylor/CJ/Vera request or exceptional-risk judgment**

### 2) Repo risk map

#### Default repos
- Start with baseline Vera review.
- Upgrade to escalated Vera review if `R >= 4`.

#### High-impact repos
`sector-feeds`, `bitregime-core`

- Default to escalated Vera review because their blast radius and operating importance are higher.
- Escalate to rare deep audit only by explicit Taylor/CJ/Vera request, exceptional-risk judgment, or intentionally selected periodic deep audit.

### 3) Rare deep audit usage

Rare deep audit is manual, never default, and not normal merge gating.

Use rare deep audit only when one of these is true:

- explicit Taylor/CJ/Vera request,
- exceptional risk or high blast radius,
- periodic sample intentionally chosen for assurance.

There is no fixed daily quota in this guidance. Add automation later only if review misses or bypasses become frequent enough to justify it.

### 4) Cost discipline and overuse controls

- Escalated review is the default for `sector-feeds` and `bitregime-core`; in other repos it is an escalation.
- Deep audit is manual + rare and must never be used as routine/default merge gating.
- Keep the model understandable before adding automation or stricter rules.

## Team/ruleset implementation notes

When implementing in GitHub:

1. keep maintainer teams out of the reviewer-routing default path;
2. use `@BitPod-App/veraqa` as the single CODEOWNERS route for active repos;
3. keep required review count lightweight at one approval, but use CODEOWNERS as a real VeraQA gate with stale-review dismissal, last-push approval, and admin enforcement enabled;
4. decide review depth in Vera/runtime/process, not by GitHub team name;
5. use rare deep audit only for exceptional risk, intentionally selected periodic assurance, or explicit Taylor/CJ/Vera request; never as default.

## PR readiness and draft policy

Default to a normal pull request when the change is intended to be review-ready.

Use a draft pull request only when the work is genuinely incomplete, exploratory, waiting on required validation, or intentionally opened as an early checkpoint. The PR body should state what is missing before it can be marked ready for review.

Do not use draft status as a default safety habit for finished work. If validation has run and the author believes the change is ready for review, open a normal PR.

## Recommended next actions

1. Move maintainer gating references (`core-maintainers` / `code-maintainers`) out of reviewer-routing defaults.
2. Keep maintainer teams as write-only maintainers.
3. Set/keep `@BitPod-App/veraqa` as the reviewer routing source.
4. Keep bypass guidance lightweight: admins may bypass when needed and should leave a short visible reason when QA is skipped.
5. Revisit stricter automation only if bypasses or routing misses become frequent.

## Out of scope

- Changing non-review access roles without a dedicated access review.
- Replacing repo-level ownership decisions.
- Full merge-policy decisions that still rely on explicit CJ acceptance paths for exception handling.
