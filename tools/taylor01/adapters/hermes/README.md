# Hermes Adapter Layer

Hermes is the preferred Taylor01 agent-runtime coordination path.

## Canonical home target

The canonical machine-local Hermes home is `$HOME/.hermes`.

Ticket-shaped homes such as `$HOME/.hermes-bit472` are temporary proof/migration sources only. Do not add new active references to them in repo docs or runtime contracts.

## Target agent model

- `default` / Hermes: internal ops, routing, paper trail, dashboard-side coordination.
- `taylor01`: PM/chief-of-staff/orchestration support.
- `vera`: QA/release integrity and PR review gate support.

## Rules

- Keep Hermes first for Taylor01/Vera workflow experiments.
- Keep Codex-on-Mini as the normal coding executor unless a later proof changes that.
- Do not treat OpenClaw as a fallback or alternate runtime.
- Use `$HOME`/env-driven references instead of person-specific absolute paths in portable docs.
- Keep secrets and OAuth caches out of repo docs.

## Read next

- `vera/README.md`
- `linear/docs/process/hermes_first_closure_migration_gate_v1.md`
