# Vera Hermes-First Execution Path

This directory defines the preferred Hermes-first execution path for Vera.

Canonical Vera identity home:
- `taylor01-mind/agents/vera/SOUL.md`

> Deprecated BIT-614 path: the legacy Vera core/adapter files under `tools/taylor01/core/agents/vera/` and `tools/taylor01/adapters/openai/vera/` were removed from canonical `main`. Current Vera identity canon lives in `taylor01-mind/agents/vera/SOUL.md`. Current operational gating belongs to the Hermes/Linear runtime, not the retired OpenAI bridge.

## Current truth

- Hermes is the preferred execution-path owner for Vera.
- Vera's identity canon lives in `taylor01-mind/agents/vera/SOUL.md`; this repo keeps Linear/Hermes gate contracts and historical adapter notes.
- The old checked-in OpenAI-native Vera adapters were removed from canonical `main` by BIT-614.
- This directory is a contract surface until a verified Hermes runner or adapter is checked in.
- OpenClaw is not a fallback or alternate runtime for Vera.

## Required Hermes execution contract

A Hermes Vera execution must preserve:

- exact verdicts: `PASSED`, `FAILED`, `NO_VERDICT`
- exact required artifacts: `verification_report.md`, `manifest.json`
- separate `Vera QA - Runtime` secret boundary
- evidence-first review behavior
- fail-closed behavior when target, context, provider output, or runtime integrity is insufficient
- explicit provenance on external comments, for example `[agent: Vera][skill: PR QA Review][runtime: Hermes]`

## QA review modes

Vera should declare the selected review mode:

- `blocker-review`: shallow review used only to unblock a formal gate on small, low-risk changes.
- `standard-review`: normal review of diff, linked issue, tests, and acceptance criteria.
- `deep-review`: stronger model/reasoning/tool use for high-risk code, security/auth/secrets/runtime work, broad refactors, migrations, or CJ-requested scrutiny.

A managed code-review product may be additional evidence, but it must not replace Vera's own verdict.

## Bridge rule

Until a verified Hermes runner exists in this repo, Hermes-first dispatch must not claim support from the retired OpenAI-native adapters. Any future bridge must preserve the Vera contract and identify its real runtime provenance.
