# Eval + Regression Gate Framework v1

## Purpose

Create a minimal, runnable eval baseline so specialist outputs can be checked consistently and regressions become visible over time.

## Eval categories

### Planning quality

Checks whether planning artifacts include:

- objective
- scope boundaries
- outputs
- verification path

### Implementation quality

Checks whether implementation artifacts:

- validate successfully
- reference evidence
- avoid broken example files

### QA quality

Checks whether QA artifacts:

- produce explicit pass/fail outcomes
- include evidence
- stay independent from implementation claims

### Handoff quality

Checks whether handoffs include:

- target owner
- deliverables
- blockers
- next-step clarity

## Baseline command bundle

The baseline eval runner executes:

1. existing unit/integration test bundle
2. runtime contract validator if present
3. memory proposal validator if present
4. governance policy validator if present
5. report generation

## Initial thresholds

- any validator failure => overall `FAIL`
- any test failure => overall `FAIL`
- missing optional validator => `WARN`, not `FAIL`

## Phase-gate use

- planning/contract lanes may ship with `PASS` or `PASS_WITH_WARNINGS`
- high-impact runtime or governance lanes should require full `PASS`

## Initial implementation artifacts

- eval contract: `linear/protocol/configs/eval-regression-gate-framework-v1.md`
- eval registry: `linear/contracts/eval_registry_v1.json`
- runner: `linear/scripts/run_eval_regression_bundle.sh`
- sample report: `linear/examples/eval_regression_report_sample_2026-03-10.md`
