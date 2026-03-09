# Capability-State + Truth-Label Incident Protocol v1

Status: Active
Owner: Product Development
Related: BIT-33
Date: 2026-03-03
Last updated: 2026-03-09
Scope: Migration execution, high-volume task fan-out, MCP/tooling instability

## Threat Focus

### Threat T1: Hidden capability regression during active execution
- Failure mode: agent silently loses capability (auth/session/tool connectivity) but continues acting as if fully operational.
- Impact: fabricated certainty, incorrect updates, dead threads, and workflow drift.
- Trigger signals:
  - repeated task failures with inconsistent root-cause claims
  - stale or conflicting status statements across channels
  - inability to complete previously-routine operations (commenting, issue lookup, thread continuation)

### Threat T2: Certainty inflation under ambiguity
- Failure mode: claims are presented as facts without verification source or confidence.
- Impact: user trust erosion, bad operational decisions, compounding recovery time.

## Mandatory Capability States

- `FULL`: end-to-end operations verified in current session.
- `DEGRADED`: partial capability available; at least one required path failing.
- `SEVERELY_IMPAIRED`: critical path failing; cannot safely continue normal execution.
- `DISCONNECTED`: cannot verify or execute required paths at all.

Rule: if evidence is mixed, pick the worse state until re-verified.

## Truth Labels (required on capability-critical claims)

- `Verified (X%)`: directly tested in-session with observable result.
- `Inferred (X%)`: reasoned from indirect evidence; not directly tested.
- `Unknown (X%)`: insufficient evidence; do not claim functionally complete.

Rule: no unlabelled certainty claims for auth, integrations, task execution health, or incident root cause.

## Incident Response Protocol

1. Declare state immediately before continuing work.
2. Record failing command/path + exact observable error.
3. Run max 3 hypothesis tests.
4. If confidence remains <30% after 3 failed tests:
   - downgrade state to `SEVERELY_IMPAIRED` or `DISCONNECTED`
   - stop speculative debugging
   - switch to workaround/quarantine mode
5. Provide explicit operator choices:
   - continue with workaround
   - pause and re-auth/reconnect
   - isolate subsystem and proceed on unaffected scope

## No Burden-Shift Default

Agent executes all steps that do not require user-only ownership (e.g., OAuth/browser approval, secret entry in user-owned vault, external dashboard clicks requiring personal session).

When user action is required, request the smallest exact action and resume immediately after.

## Audit Integrity Rule

If asked to run a specific audit mode, run exactly that mode or explicitly decline with:
- why it cannot be run as requested
- what alternative can be run now
- confidence and limitations of that alternative

## Evidence Format (minimum)

- `state`: one of FULL/DEGRADED/SEVERELY_IMPAIRED/DISCONNECTED
- `claim`: statement being made
- `truth_label`: Verified/Inferred/Unknown + %
- `evidence`: command/API test/log line reference
- `next_action`: immediate execution step

## Operational Checklist for New Sessions

1. Declare current capability state.
2. Smoke-test critical integrations (Linear, GitHub, bridge/runtime where applicable).
3. Label all capability-critical claims.
4. On first critical failure, enter incident protocol.
