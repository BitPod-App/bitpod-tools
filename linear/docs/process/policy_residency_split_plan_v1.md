# Policy Residency Split Plan v1

Status: Draft — awaiting CJ review
Owner: Taylor01 / CJ
Related: BIT-298
Last updated: 2026-05-29
Scope: Staged plan to separate durable Taylor01 cognitive policy canon from org-level adapter/governance surfaces

## Objective

Define a staged plan to separate durable Taylor01 cognitive policy canon from org-level adapter and governance surfaces.

## Why This Exists

Current policy concentration in `bitpod-docs` is useful for org governance, but does not yet cleanly express what should live in `taylor01-mind` versus what should remain adapter-only in org/runtime repos.

This creates risk of:

- cognitive policy and org governance becoming entangled (hard to version independently)
- runtime adapters accidentally becoming policy authors
- no clear ownership when policy needs to evolve

## Residency Map

Every policy class must have exactly one canonical home.

| Policy class | Primary home | Adapter copies allowed? | Runtime consumption path | Notes |
| -- | -- | -- | -- | -- |
| Cognitive reasoning principles (how Taylor thinks) | `taylor01-mind` | No canon copy; pointer-only | Runtime loads via adapter pointer to mind canon | Durable cognitive authority |
| Memory/recall doctrine | `taylor01-mind` | No canon copy; pointer-only | Runtime memory contract references mind policy IDs | Keep versioned IDs stable |
| Agent behavior standards (epistemic, decision style) | `taylor01-mind` | Adapter excerpt only when required | Runtime references named policy surfaces | Excerpts must declare source + version |
| Workspace governance/prohibitions (cross-repo) | `bitpod-docs` | Mirror packets as needed | Repo `AGENTS.md` → bitpod policy canon | Remains org-level authority |
| Security/secrets handling (org baseline) | `bitpod-docs` | Controlled mirror allowed | Same as above | Org policy wins unless explicit exception |
| Runtime bootstrap discovery contract | `taylor01-runtime` contract docs | Adapter shim only | Root `AGENTS.md` first, then referenced canon, then runtime adapter | No `.codex`-only authority |
| Provider-specific wiring (Codex/Gemini/Hermes adapters) | Runtime repo adapter layer | Yes (runtime-local) | Adapter resolves to same canon chain | Never policy-authoring surfaces |
| Mission Control/operator UI behavior constraints | `taylor01-runtime` | No external canon fork | Runtime contract docs | Keep utility/recovery boundaries explicit |

## Migration Principles

1. **Single authority per policy class**: every policy class has one canonical home.
2. **Adapter-not-authority**: adapters can point, map, and validate; they do not define new canon.
3. **No silent divergence**: if a local adapter excerpt exists, it must include source URI/path + version/hash.
4. **Fail loudly on missing canon**: runtime must error when canonical chain cannot be resolved.
5. **Versioned IDs before moves**: policy IDs must be stable before relocation to avoid reference breakage.

## Phased Plan

### Phase P0 — Inventory + Tagging

- Enumerate current policy files in `bitpod-docs`
- Tag each by class (`mind`, `org`, `runtime-adapter`)
- Identify mixed files that need splitting

### Phase P1 — Canon Declaration

- Declare canonical home for each class
- Define owner + review authority per class
- Freeze creation of new mixed-scope policy files

### Phase P2 — Adapter Rewiring Plan

- Define pointer schema from runtime/org adapters to mind canon
- Define required adapter compliance evidence
- Create migration checklist per affected repo

### Phase P3 — Controlled Migration

- Move selected mind policies to `taylor01-mind`
- Leave redirect/pointer stubs where necessary
- Run consistency validation across Codex + Hermes lanes

### Phase P4 — Post-Migration Hardening

- Remove temporary stubs after validation window
- Enforce lint/check that blocks duplicate canon introduction
- Publish final residency registry

## Verification Gates

- **G1**: Every policy class has one declared canonical home
- **G2**: All adapter pointers resolve to existing canon
- **G3**: No duplicate canon docs for same policy ID
- **G4**: Runtime bootstrap tests fail on broken canon paths
- **G5**: Cross-lane behavior remains consistent on real orchestration tasks

## Open Questions

- Should the truthfulness policy family remain fully org-canon in `bitpod-docs`, or should core cognitive pieces move to `taylor01-mind` with org wrappers?
- Do we want a machine-readable residency registry file (TOML/YAML) in addition to docs?
- What minimum compatibility window is required for adapter stubs after policy relocation?

## Sequencing Constraint

Defer implementation until Codex orchestration lane is green in embodied runtime testing.

This is a planning document only. Implementation follows a later phase.

## Non-Goals

- No immediate mass policy migration
- No replacement of Codex lane contracts
- No broad portability redesign in the same pass
