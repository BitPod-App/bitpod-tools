# Linear Issue Type Decision Guide v1

Status: Active canonical BitPod guide
Owner: Product Development
Last updated: 2026-04-28
Applies to: Product Development `Issue Type` selection, correction, and hygiene audits
Related canon: `linear_operating_model_v1.md`, `linear_operating_guide_v3.md`, `linear_issue_template_evidence_contract_v2.md`

## Purpose

Use this guide to choose, correct, and audit exactly one Linear `Issue Type` in a repeatable, evidence-based way.

This guide is deliberately narrow. It does not redesign the taxonomy. It explains how to use the existing types: `Plan`, `Feature`, `Bug`, `Chore`, `Design`, and `Release`.

This is the current active BitPod Linear process rubric. It may later be extracted into Taylor01/Hermes skills, but until that extraction exists this file is the canonical workspace guide.

## Core rule

Classify by the substance of the work, not by title wording.

- Do **not** infer type from the issue title alone.
- Treat the title as a weak hint only.
- Body, scope, acceptance criteria, comments, linked PRs, merged code, and review evidence matter more.
- If the title conflicts with implementation or acceptance evidence, evidence wins.
- If evidence is too thin, flag ambiguity instead of pretending certainty.

## Evidence hierarchy

Use the strongest available evidence in this order:

1. GitHub PR diff, merged code, commit history, and attached artifacts.
2. PR title/body, review context, and explicit issue links.
3. Linear description, scope, acceptance criteria, comments, and parent/child context.
4. Issue title, only as a weak hint.
5. Best judgment, only when evidence is incomplete but still sufficient to explain the decision.

If a correction depends mostly on item 4 or weak item 5, leave a comment noting the ambiguity rather than silently normalizing.

## Operational definitions

| Type | Use when | Do not use when |
|---|---|---|
| `Bug` | The primary work fixes broken behavior, a regression, or a defect against expected behavior. | The work adds a capability that never existed, even if the title says "fix". |
| `Feature` | The primary outcome is a non-trivial new or enhanced user-facing or team-facing capability. | The work is only cleanup, docs, audit, dependency work, or prep with no shipped capability. |
| `Chore` | Maintenance, cleanup, dependency upgrades, refactors, docs-only work, audits, process/tooling upkeep, or enabling/prep work without new functionality. | The same PR also shipped a real capability; split Chore and Feature tickets when practical. |
| `Design` | The primary purpose is actual GUI, graphic design, visual branding, UI/UX, design-system, or implementation of linked design assets, usually Figma. | The work is code architecture, backend architecture, system design, technical design, planning, or docs that merely use the word "design". |
| `Plan` | The ticket is a parent rollout / epic-like container for a larger coherent effort, and the actionable work is completed through child issues. The parent is non-actionable except through child completion. | The ticket is itself the actionable implementation task. |
| `Release` | The ticket is a coordinated shipping object with a real release date, rollout scope, release checklist, version bump, or multi-feature ship gate. | The ticket is just a feature, PR, deployment task, or merged implementation with no release coordination object. |

### Narrow `Design` test

Use `Design` only if the answer is yes:

> Does this include actual GUI or graphic design, and is the primary goal to improve UI/UX or visual branding by implementing or producing the linked design asset?

If no, do not use `Design`.

### Narrow `Release` test

Use `Release` rarely. A true `Release` should usually include a real release date or release window, coordinated rollout scope, and shipping checklist.

A `Release` issue should not move through normal implementation closure just because constituent PRs merged. Treat it as a release gate: acceptance and closure require release-readiness evidence, not only code evidence.

For now, a true `Release` should block normal `Delivered` -> `Accepted` or `Done` progression until the release gate, PM decision, and shipping evidence are explicit.

## Decision tree

1. Is the ticket only a parent container whose child issues are the real tasks?
   - Yes -> `Plan`.
2. Is it a coordinated ship/release object with real rollout scope, date/window, checklist, or version bump?
   - Yes -> `Release`.
3. Is the primary work actual GUI/graphic/visual branding/UI-UX work, usually against linked design assets?
   - Yes -> `Design`.
4. Is the primary work fixing broken or regressed expected behavior?
   - Yes -> `Bug`.
5. Did the work ship a meaningful new or enhanced capability for users or the team?
   - Yes -> `Feature`.
6. Is the work maintenance, cleanup, docs, audit, refactor, dependency, process, or enabling/prep work without new capability?
   - Yes -> `Chore`.
7. If the answer is mixed:
   - Split into separate typed tickets when practical, even when they share the same PR.
   - If retroactive splitting is not practical, classify by the dominant shipped outcome and leave a comment explaining the evidence.
8. If evidence is weak:
   - Do not force a type. Keep/set `needs-type` or leave a normalization comment with the missing evidence.

## Retroactive correction rules

Use these during hygiene audits, PR closeout, and after-the-fact ticket normalization.

- If the PR clearly shipped a capability, classify by what actually shipped.
- If the work was docs/spec/audit/cleanup/refactor/dependency/process/enabling-only work, use `Chore`.
- The closeout status class `docs/design/audit` does not automatically mean Issue Type `Design`; most docs/audit/process work is `Chore`.
- If the work fixed broken behavior, use `Bug` even when the title says "feature".
- If the work implemented linked UI/UX or visual design assets, use `Design`; otherwise technical "design" is not `Design`.
- If one PR includes both enabling work and shipped capability, prefer separate `Chore` and `Feature` tickets linked to the same PR.
- If a parent ticket is only an umbrella whose completion comes from child tickets, use `Plan` even if the title sounds like a feature.
- If the body says one thing but the diff/artifacts show another, evidence wins.
- If there is no GitHub link, use the Linear body/comments and parent context; if those are thin, flag ambiguity.
- For historical `Done` / `Accepted` tickets with no estimate, do not invent points unless the sizing is obvious from the evidence and the cleanup pass explicitly authorizes backfill.
- Ambiguous historical cases can remain unresolved. A truthful ambiguity comment is better than a fake-clean audit.

## Hygiene audit checklist

For each issue in a hygiene audit:

1. Confirm there is exactly one canonical `Issue Type`.
2. Review the strongest evidence available, especially linked PRs and merged code.
3. Apply the decision tree.
4. Correct only when the evidence supports the correction.
5. If correction is ambiguous, leave `needs-type` or a comment explaining the evidence gap.
6. Do not change estimate, priority, owner, or milestone just to make the audit look complete.
7. Add one concise normalization comment if the correction is non-obvious.

Minimum audit mapping column:

| Issue | Current type | Evidence reviewed | Decision | Confidence / ambiguity |
|---|---|---|---|---|

## Normalization comment template

```md
Issue Type normalization:
- Evidence reviewed: <PR/diff/body/comments/artifacts>
- Decision: <Bug | Feature | Chore | Design | Plan | Release | left ambiguous>
- Rationale: <one sentence; evidence beats title if they conflict>
- Follow-up: <none | needs-type | needs-estimate | split tickets | missing PR link>
```

## Recent hygiene examples

These examples are lightweight precedents, not permanent overrides. Re-check evidence when re-auditing.

| Case | Decision pattern | Why |
|---|---|---|
| BIT-212 from the BIT-270 cleanup family | `Chore` | Supporting/cleanup work was normalized as maintenance rather than a shipped capability. |
| BIT-282 from the BIT-270 cleanup family | `Chore` | Retroactive metadata cleanup added missing type/estimate for supporting work. |
| BIT-283, BIT-303, BIT-304 from the BIT-270 cleanup family | `Feature` | The cleanup record says code/runtime reality had already shipped capability. |
| BIT-270-style parent rollout tickets | Check for `Plan` before preserving `Feature` | If the parent is only an umbrella and children are the executable work, the guide points to `Plan`. |
| BIT-35-style live admin/config lanes | Usually `Chore` | Workflow/admin/config/process upkeep is enabling work, not a product feature or `Design`. |

## Open questions / edge cases

Leave these explicit instead of silently resolving them:

- Retroactive PR-backed tickets with thin body text: use best judgment only when PR evidence is strong enough to explain; otherwise leave ambiguous.
- `Done` / `Accepted` tickets with no estimate: backfill only when sizing is obvious and authorized for that cleanup pass; otherwise flag rather than guess.
- Multiple PRs on one issue: classify by dominant outcome only when clear; otherwise split tickets or leave an edge-case comment.
- No GitHub link: classify from Linear evidence only if sufficient; otherwise mark missing evidence.
- Title/body conflicts: implementation and acceptance evidence win.
- Scaffold/enabling work that shipped real capability: `Feature` if the primary accepted outcome is usable capability; `Chore` if it is only prep.
- Ambiguous historical cases: leave unresolved when correction would be mostly title inference or speculation.

## Automation note

Future hygiene automation should use this guide as the rubric, not as a title keyword matcher.

- `Issue Type` validation may enforce exactly one canonical type.
- Type suggestion/correction must cite evidence source(s).
- Low-confidence suggestions should produce `needs-type` or an ambiguity comment, not an automatic correction.
- The PR-to-Linear mapping table should include an `Issue Type decision` column for normalization runs.
