# GitHub Org Baseline Policy v1

Status: Draft v1 (Phase 1)
Owner: PM/Platform
Implements: BIT-23
Consumed by: BIT-11
Last updated: 2026-03-09

## Scope
Applies to GitHub organization `BitPod-App` and all repos under the org.

## Security Minimums
- Require 2FA for all organization members.
- Private repositories by default; public exposure allowed only by explicit PM/owner decision.
- Restrict repository creation/deletion to owners/admin-approved roles.
- Enforce branch protection/rulesets on default branches.
- Enable security scanning baseline across repos (secret scanning, dependency graph, Dependabot alerts).

## Team and Permission Model
- `Owners`: full org admin and billing-critical controls.
- `Platform Admin`: manage org settings/security policy (no billing changes unless approved).
- `Engineers`: write access only to assigned repos.
- `Agents`: scoped write access only where explicitly required.
- `ReadOnly`: stakeholder visibility without mutation permissions.

## Secrets Strategy
- Org-level secrets: shared non-env-specific automation keys.
- Repo-level secrets: runtime-specific keys that are not broadly reusable.
- Environment secrets: production/staging separation where workflows support environments.
- Never store raw secret values in issues/comments/docs.

## Policy-to-Setting Mapping
| Policy Control | GitHub Setting Path | Target Value |
|---|---|---|
| Enforce MFA | Org Settings -> Security -> Authentication security | Require 2FA = On |
| Default repo visibility | Org Settings -> Member privileges / Repository defaults | Private by default |
| Public repo exception policy | Org-level decision log + repo settings | Only explicitly approved repos can be public |
| Restrict repo creation | Org Settings -> Member privileges | Limited to approved roles |
| Restrict repo deletion/transfer | Org Settings -> Repository administration | Owners/Admin only |
| Branch protection baseline | Repo Settings -> Branches / Rulesets | Protect default branch; require PR for merge |
| Secret scanning | Repo Settings -> Security & analysis | Enabled |
| Dependency graph | Repo Settings -> Security & analysis | Enabled |
| Dependabot alerts | Repo Settings -> Security & analysis | Enabled |

## Evidence Requirements for Completion
- Capture command/UI proof per control.
- Record pass/fail for each mapped setting.
- Record any temporary deviations with owner and follow-up issue.

## Risk and Deviation Log
- Some org-wide controls may require owner-only actions.
- Automation behavior in Linear statuses can drift; completion truth remains evidence-based.

## Phase 1 Completion Gate (for BIT-23)
- This document exists in versioned path.
- Mapping table is complete.
- BIT-11 references this file as implementation source.
- Any unresolved controls are explicitly listed with follow-up issues.
