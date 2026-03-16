# Engineering Specialist Lane Contract v1

Status: Working baseline  
Linked issue: [BIT-93 — Stand up first engineering specialist lane under Taylor-led delegation](https://linear.app/bitpod-app/issue/BIT-93/stand-up-first-engineering-specialist-lane-under-taylor-led-delegation)

## Objective

Define the first real engineering specialist lane as a distinct operating lane under Taylor-led delegation so engineering is no longer implied only by generic Codex execution.

This contract does not claim a fully separate multi-engineer runtime yet. It defines the first bounded engineering lane that can receive delegated work, produce implementation artifacts, and return reproducible validation evidence.

## Lane identity

Current working identity:

- lane name: Engineering Specialist
- operating mode: Taylor-dispatched implementation lane
- current implementation surface: Codex operating as the bounded engineering executor for delegated tasks

Durable intent:

- engineering remains a distinct lane even if the present execution surface is still Codex-backed
- future expansion may split this into multiple engineering specialists or a more explicit engineering runtime

## Role boundaries

### Engineering owns

- implementation of scoped code/config/docs changes
- execution of validation commands within the delegated scope
- production of reproducible implementation artifacts
- explicit reporting of blockers, residual risk, and rollback expectations

### Engineering does not own

- product priority or final scope decisions
- independent QA verdict authority
- final completion/go-no-go recommendation
- rewriting the acceptance contract after execution has started

## Required handoff from Taylor

Each engineering delegation must include:

1. objective
2. in-scope
3. out-of-scope
4. required outputs
5. validation commands/checks
6. artifact destination path(s)
7. rollback note
8. escalation rule

This inherits the baseline from:

- [taylor-orchestrator-contract-v1.md](./taylor-orchestrator-contract-v1.md)
- [agent-handoff-templates-v1.md](../templates/agent-handoff-templates-v1.md)

## Required output contract

Every engineering-lane execution must return:

1. implementation output
   - code, config, docs, or runtime changes
2. validation evidence
   - exact command(s) run and observed result
3. durable artifacts
   - repo paths, run artifacts, PR links, or issue links
4. residual-risk note
5. rollback path when relevant

Engineering work does not count for lane proof if it ends as:

- generic "Codex changed files"
- no delegated objective
- no reproducible validation evidence
- no durable artifact path back into Taylor/issue flow

## Minimum operating flow

1. Taylor decomposes the task and delegates to Engineering.
2. Engineering executes only within the bounded scope.
3. Engineering records implementation output and validation evidence.
4. QA validates behavior/release confidence when required.
5. Taylor synthesizes the result back into the issue/phase spine.

## Fallback model for current bootstrap reality

Current recommendation:

- one real engineering lane is sufficient for bootstrap Phase 4 proof if:
  - the lane is explicitly delegated by Taylor
  - outputs are reproducible
  - QA remains independent

Bounded fallback model:

- one primary engineering lane
- Taylor handles decomposition and gating
- Vera handles independent QA

This is acceptable for the current minimum-team proof.

It is not the final scaling model for a larger multi-agent engineering team.

## Completion signal for BIT-93

[BIT-93 — Stand up first engineering specialist lane under Taylor-led delegation](https://linear.app/bitpod-app/issue/BIT-93/stand-up-first-engineering-specialist-lane-under-taylor-led-delegation) is satisfied only when:

- this contract or equivalent operating note exists
- at least one real delegated execution record exists under this lane
- that record includes linked implementation output and reproducible validation evidence
- the repo explicitly states whether one lane plus fallback is enough for current bootstrap reality
