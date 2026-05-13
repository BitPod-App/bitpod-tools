# Vera Hermes-First Execution Path

This directory defines the preferred Hermes-first execution path for Vera.

Canonical Vera home:
- `tools/taylor01/core/agents/vera`

## Current truth

- Hermes is the preferred execution-path owner for Vera.
- Vera's portable core remains the source of truth for identity, verdicts, artifacts, and guardrails.
- The currently checked-in executable Vera adapters still live under `../openai/vera/`.
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

Until a verified Hermes runner exists in this repo, Hermes-first dispatch may bridge to the current OpenAI-native adapters only if the bridge preserves the portable Vera contract and does not claim Hermes-native execution that did not happen.
