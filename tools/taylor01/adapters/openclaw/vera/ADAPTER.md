# OpenClaw Mapping For Vera

## Purpose

Record the retired OpenClaw mapping shape so stale artifacts are not mistaken for active strategy.

OpenClaw is not a fallback, alternate runtime, or future execution target for Vera. Hermes-first is the active direction.

## Inputs that older mappings referenced

- `tools/taylor01/core/agents/vera/AGENTS.md`
- `tools/taylor01/core/agents/vera/IDENTITY.md`
- `tools/taylor01/core/agents/vera/SOUL.md`
- `tools/taylor01/core/agents/vera/OUTPUT_CONTRACT.md`
- `tools/taylor01/core/agents/vera/SECRETS.md`

## Closure responsibilities

- preserve historical context without reviving OpenClaw as a runtime
- keep OpenClaw-specific config, routing, packaging, and secrets out of Vera's canonical core
- point active Vera execution work to Hermes-first or current OpenAI-native bridge adapters

## Explicitly not done here

- no claim that a full OpenClaw-native Vera runtime is installed
- no claim that `.openclaw` is Vera's permanent home
- no OpenClaw-specific secret reuse from Taylor
- no follow-on task to wire Vera into OpenClaw

## If old material conflicts

The active authority order is:

1. `tools/taylor01/core/agents/vera/`
2. `tools/taylor01/adapters/hermes/vera/`
3. `tools/taylor01/adapters/openai/vera/`
4. this historical OpenClaw closure note
