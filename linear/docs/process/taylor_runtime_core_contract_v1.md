# Taylor Runtime Core Contract v1

Status: Working baseline
Linked issue: [BIT-67 — Taylor runtime core hardening: orchestration loop + agent/tool registry v1](https://linear.app/bitpod-app/issue/BIT-67/taylor-runtime-core-hardening-orchestration-loop-agenttool-registry-v1)

## Objective

Define the runtime contract for Taylor as the central orchestrator so delegation, capability degradation, and tool use follow a repeatable state machine.

## Runtime Invariants

- Taylor is the only broad-scope orchestrator.
- Specialists do not self-route work across the system.
- Linear remains the execution system of record.
- Communication surfaces are adapters, not the database.
- Degraded capability must be recorded before fallback behavior starts.

## State Machine

1. `intake`
2. `plan`
3. `dispatch`
4. `await_results`
5. `verify`
6. `synthesize`
7. `complete`
8. `escalate`

Allowed degraded overlays:

- `degraded`
- `severely_impaired`
- `disconnected`

## State Requirements

### intake
- Accept CJ request or system trigger.
- Resolve current issue/project context if relevant.
- Record capability state snapshot.

### plan
- Convert intent into one or more bounded tasks.
- Define owner lane, validation path, and rollback note.
- Reject fuzzy requests that cannot be scoped safely.

### dispatch
- Emit one delegation packet per specialist task.
- Include required outputs, acceptance checks, and artifact path.
- Bind only the minimum tool set needed for the task.

### await_results
- Wait for specialist output or blocker signal.
- Do not mutate task scope implicitly while waiting.

### verify
- Run validation commands or collect QA evidence.
- Classify claims as Verified, Inferred, or Unknown.
- Fail closed on missing high-impact evidence.

### synthesize
- Translate low-level results into CJ-facing or system-facing summary.
- Prepare Linear updates, artifact links, and residual-risk note.

### complete
- Mark the work ready for closeout only when evidence is attached.

### escalate
- Triggered by security risk, authority ambiguity, destructive action, or unresolved capability degradation.

## Delegation Packet Minimum

- `task_id`
- `objective`
- `owner_lane`
- `inputs`
- `required_outputs`
- `validation`
- `artifacts`
- `rollback`
- `escalation_rule`

## Capability-State Handling

Before any fallback:

1. record `capability_state`
2. record `truth_classification`
3. record `certainty_pct`
4. choose minimum-safe workaround
5. escalate if the workaround changes authority, security, or audit quality

## Registry Binding

Runtime behavior depends on these machine-readable artifacts:

- `/Users/cjarguello/bitpod-app/bitpod-tools/linear/contracts/runtime_states_v1.json`
- `/Users/cjarguello/bitpod-app/bitpod-tools/linear/contracts/agent_registry_v1.json`
- `/Users/cjarguello/bitpod-app/bitpod-tools/linear/contracts/tool_registry_v1.json`
- `/Users/cjarguello/bitpod-app/bitpod-tools/linear/examples/taylor_delegated_trace_v1.json`

## Non-Goals

- replacing Linear as source of record
- making Discord mandatory
- allowing free-form agent-to-agent chatter without Taylor routing
