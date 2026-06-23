# OpenClaw Mapping For Vera

## Purpose

Record the retired OpenClaw mapping shape so stale artifacts are not mistaken for active strategy.

OpenClaw is not a fallback, alternate runtime, or future execution target for Vera. Hermes-first is the active direction.

## Inputs that older mappings referenced

> Deprecated BIT-614 path: the legacy Vera core/adapter files under `tools/taylor01/core/agents/vera/` and `tools/taylor01/adapters/openai/vera/` were removed from canonical `main`. Current Vera identity canon lives in `taylor01-mind/agents/vera/SOUL.md`. Current operational gating belongs to the Hermes/Linear runtime, not the retired OpenAI bridge.

Historical OpenClaw mapping material referenced these deleted files:

- `tools/taylor01/core/agents/vera/AGENTS.md`
- `tools/taylor01/core/agents/vera/IDENTITY.md`
- `tools/taylor01/core/agents/vera/SOUL.md`
- `tools/taylor01/core/agents/vera/OUTPUT_CONTRACT.md`
- `tools/taylor01/core/agents/vera/SECRETS.md`

## Closure responsibilities

- preserve historical context without reviving OpenClaw as a runtime
- keep OpenClaw-specific config, routing, packaging, and secrets out of Vera's canonical core
- point active Vera execution work to Hermes-first / Linear gate runtime surfaces, not the retired OpenAI-native bridge adapters

## Explicitly not done here

- no claim that a full OpenClaw-native Vera runtime is installed
- no claim that `.openclaw` is Vera's permanent home
- no OpenClaw-specific secret reuse from Taylor
- no follow-on task to wire Vera into OpenClaw

## If old material conflicts

The active authority order is:

1. `taylor01-mind/agents/vera/SOUL.md` for Vera identity canon
2. `bitpod-tools/linear/docs/process/vera_qa_lane_contract_v1.md` and related Linear/Hermes gate docs for QA lane behavior
3. `tools/taylor01/adapters/hermes/vera/` for Hermes-first adapter notes
4. this historical OpenClaw closure note

The deleted `tools/taylor01/core/agents/vera/` and `tools/taylor01/adapters/openai/vera/` paths are historical inputs only.
