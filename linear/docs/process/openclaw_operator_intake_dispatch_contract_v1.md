# OpenClaw Operator Intake And Dispatch Contract v1

Status: Active Phase 4 contract
Primary issue: [BIT-114 — Define OpenClaw-native operator intake and dispatch surface](https://linear.app/bitpod-app/issue/BIT-114/define-openclaw-native-operator-intake-and-dispatch-surface)
Related issues:
- [BIT-115 — Prove personal-computer -> OpenClaw HQ conversational/dispatch loop](https://linear.app/bitpod-app/issue/BIT-115/prove-personal-computer-openclaw-hq-conversationaldispatch-loop)
- [BIT-122 — Supporting chat-adapter parity for Discord and other messaging surfaces](https://linear.app/bitpod-app/issue/BIT-122/supporting-chat-adapter-parity-for-discord-and-other-messaging)
- [BIT-104 — Execute Mac Mini execution-HQ bootstrap for NemoClaw runtime](https://linear.app/bitpod-app/issue/BIT-104/execute-mac-mini-execution-hq-bootstrap-for-nemoclaw-runtime)
- [BIT-110 — Validate first AI HQ runtime path and complete first truthful smoke workflow](https://linear.app/bitpod-app/issue/BIT-110/validate-first-ai-hq-runtime-path-and-complete-first-truthful-smoke)
- [BIT-205 — Define Taylor01 operator intake and supporting surface adapters](https://linear.app/bitpod-app/issue/BIT-205/define-taylor01-operator-intake-and-supporting-surface-adapters)

## Purpose

Define the primary operator interaction contract for the OpenClaw / AI HQ era so
Phase 4 can proceed with one explicit control path instead of drifting between
Discord habits, local-machine habits, and ambiguous "future dashboard" ideas.

This contract is intentionally practical. It defines the operator path that can
be used now, while preserving room for a cleaner UI later.

## Verified starting constraints

- `MacBook` remains the control console, not the primary execution host.
- `Mac Mini` execution account remains the real HQ execution environment.
- first truthful HQ smoke proof already exists under the execution-account path
  from the Phase 3 spine
- final AI-agent operability is still gated by
  [BIT-173 — Final legacy secret removal and 1Password cutover gate before AI agent operability](https://linear.app/bitpod-app/issue/BIT-173/final-legacy-secret-removal-and-1password-cutover-gate-before-ai-agent)
- supporting chat surfaces may remain useful, but they are not allowed to
  redefine the HQ truth model

## Primary operator surface

The primary operator surface for the current OpenClaw HQ era is:

1. operator starts from the personal computer control console
2. operator anchors or selects work in Linear
3. operator reaches the HQ through the intended remote path into the execution
   environment
4. work runs in the HQ runtime boundary
5. durable outcomes are written back to Linear and repo-owned truth surfaces

This means the primary surface is not:

- Discord
- a local MacBook runtime pretending to be HQ
- a dashboard that does not yet exist
- ad hoc recollection from prior chat threads

## Intake contract

### Start new work

Use this minimum intake sequence:

1. identify the owning Linear issue or create the missing issue first
2. state the operator intent from the control console
3. execute or dispatch into the HQ runtime path
4. record the durable result back onto the issue and/or repo surface

Minimum required intake payload:

- target issue or explicit execution lane
- operator ask
- constraints or guardrails
- expected durable output

### Continue existing work

Continuations must anchor from durable truth, in this order:

1. Linear issue state and comments
2. repo state, code, docs, and artifacts
3. current HQ runtime/session state if still live
4. supporting chat context only after the above

Rule:

- do not treat Discord or a prior freeform conversation as the primary
  continuity source if Linear/repo truth disagrees or is fresher

## Dispatch contract

Dispatch means:

- the operator uses the personal computer to send work into the HQ runtime
- the HQ runtime performs the real execution
- the personal computer remains the control console and observation point

Dispatch does not mean:

- doing the real build or runtime work primarily on the personal computer
- treating a chat transport as the execution boundary
- storing the only actionable state in a transport thread

## Durable truth split

Use this split consistently:

- Linear = execution truth, scope, status, dependencies, operator decisions
- repo code/docs = implementation truth and reusable operating contract
- HQ runtime/session = active working state, temporary until materialized
- supporting chat surfaces = convenience transport only

## Supporting adapter rules

Discord and other messaging adapters may do these things:

- submit or relay an operator request
- mirror progress summaries
- link to issues, PRs, and artifacts
- provide notification or lightweight conversational access

They must not do these things:

- become the only source of work scope
- become the only place decisions live
- bypass Linear or repo truth for durable outcomes
- force the system to depend on one transport-specific behavior

## Transitional versus target-state

### Transitional now

- personal computer chat plus remote console remains the main operator bridge
- some runtime proofs may still use temporary harnesses
- adapter parity remains secondary work after the primary operator path is clear

### Target-state later

- a cleaner OpenClaw-native intake surface may replace parts of the current
  control-console UX
- supporting adapters should map onto the same intake and result contract
- no later UI should change the durable truth split above

## What this unblocks

### For BIT-114

This issue can close once this contract is accepted and the primary surface is
no longer ambiguous.

### For BIT-115

The proof loop should use this exact path:

1. operator starts from the personal computer
2. operator anchors in Linear
3. operator reaches the HQ runtime remotely
4. HQ performs work
5. result returns with durable issue/repo evidence

### For BIT-122

Supporting adapters should be judged only by whether they preserve:

- operator request entry
- durable linkback
- artifact/result return
- non-primary status

## Explicit non-goals

- no claim that Discord is the primary Phase 4 proof surface
- no requirement to wait for a future dashboard before proving the operator loop
- no reopening of the locked HQ execution boundary to satisfy UI preferences
