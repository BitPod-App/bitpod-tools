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

## Executable Telegram/Taylor01/Codex gate

Run the read-only preflight before claiming the Telegram -> Hermes Agent Taylor01 -> Codex route is executable:

```bash
python3 tools/taylor01/adapters/hermes/telegram_taylor01_codex_gate.py
```

The gate checks only observable prerequisites: canonical `$HOME/.hermes` targeting, masked Telegram token injection, `hermes` CLI availability, addressability of the `taylor01` Hermes profile, `codex` CLI availability, and absence of active OpenClaw runtime environment variables. It does not start Telegram polling, mutate Hermes home, run Codex, or claim a successful heartbeat.

## Read next

- `vera/README.md`
- `linear/docs/process/hermes_first_closure_migration_gate_v1.md`
