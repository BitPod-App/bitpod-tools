# OpenClaw Mapping For Vera

## Purpose
Project the portable Vera core into an OpenClaw-compatible runtime without making OpenClaw the architecture owner.

## Inputs to carry forward from core
- `tools/taylor01/core/agents/vera/AGENTS.md`
- `tools/taylor01/core/agents/vera/IDENTITY.md`
- `tools/taylor01/core/agents/vera/SOUL.md`
- `tools/taylor01/core/agents/vera/OUTPUT_CONTRACT.md`
- `tools/taylor01/core/agents/vera/SECRETS.md`

## Adapter responsibilities
- concatenate or map the portable core files into the OpenClaw system/agent prompt surface
- preserve PR URL as a primary self-contained review input when possible
- keep follow-up questions gated to truthfulness blockers only
- keep OpenClaw-specific config, routing, and packaging outside the core definition

## Explicitly not done here
- no claim that a full OpenClaw-native Vera runtime is already installed in this repo
- no claim that `.openclaw` is Vera's permanent home
- no OpenClaw-specific secret reuse from Taylor

## Remaining follow-on work
- wire these mappings into the actual OpenClaw package once that runtime exists as a verified codebase
- validate artifact writing and secret injection through the real OpenClaw execution path
