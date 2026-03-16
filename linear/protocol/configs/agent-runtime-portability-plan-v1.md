# Agent Runtime Portability Plan v1

Status: Working baseline  
Linked issue: [BIT-66 — Agent runtime portability plan: Cloudflare-first execution with platform-decoupled memory/integrations](https://linear.app/bitpod-app/issue/BIT-66/agent-runtime-portability-plan-cloudflare-first-execution-with)

## Objective

Keep agent execution portable so BitPod can run on Cloudflare-first infrastructure without permanent platform lock-in.

## Principles

- Core logic should not depend on a single provider runtime.
- Integrations should be adapter-based.
- Memory/state contracts should be interface-driven.
- Webhook ingress should be replaceable.

## Reference Architecture (v1)

1. Core orchestration logic
   - portable modules (`linear/src/engine.py`, `linear/src/runtime.py`)
2. Integration adapters
   - GitHub adapter
   - Linear adapter
   - storage/memory adapter
3. Transport edge
   - Cloudflare Worker ingress (`linear/cloudflare/worker.mjs`)
4. Runtime host
   - local process today, Cloudflare-compatible endpoint tomorrow

## Portability Boundaries

Provider-coupled components (keep thin):

- webhook authentication wrappers
- provider token exchange
- provider-specific SDK calls

Provider-neutral components (keep central):

- task decomposition logic
- gate rules
- evidence contract checks
- handoff schema

## Migration Stages

1. Baseline (now)
   - local runtime + dry-run logic with portable core
2. Edge ingress stabilization
   - Cloudflare Worker endpoint forwards canonical event payloads
3. Runtime move
   - deploy runtime to chosen host with same adapter contract
4. Memory abstraction hardening
   - formalize backing store interface and replay safety

## Non-Goals (Phase 1/early Phase 4)

- full production multi-region rollout
- irreversible migration cutover
- provider-specific deep optimization

## Exit Criteria for Portability Baseline

- adapter boundaries documented
- Cloudflare ingress scaffold present
- event processing behavior reproducible in simulation
- no business logic coupled directly to provider SDK internals
