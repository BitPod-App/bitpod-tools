# bitpod-tools

Shared tooling repo for BitPod App local operations, workflow automation,
and reusable operator support surfaces.

## What Belongs Here

- `linear/` - Linear workflow tooling, webhook/runtime code, and related
  process docs for the Linear tool surface.
- `gpt_bridge/` - local or remote bridge utilities for calling GPT from
  Codex and other local runtimes.
- `chatgpt-prompts/` - prompt packs and prompt assets used by tooling and
  operator workflows.
- `config/` - active tool configuration consumed by scripts and cleanup
  workflows.
- `docs/` - repo-local tooling notes and migration guardrails.
- `.worktrees/` - intentional linked worktrees for active branch isolation.

## What Does Not Belong Here

- Feed discovery, transcription, or tracked transcript artifacts. Those
  belong in `sector-feeds/`.
- Shared workspace policy, archive canon, or master indexing. Those
  belong in `bitpod-docs/`.
- Product-facing application copy or MVP narrative docs unless they are
  directly required by a tool in this repo.

## Entry Points

- `linear/protocol/configs/linear-operating-guide-v3.md`
- `gpt_bridge/README.md`
- `docs/README.md`
- `SECURITY.md`
- `bitpod-tools-threat-model.md`

## Identity Notes

- This is an operational tooling repo, not the main product repo.
- Some paths still carry historical `bitpod` naming from migration-era
  repo renames. Treat repo purpose, not leftover names, as canonical.
- If a document here is repo-local and tool-specific, it can live here.
  If it is shared workspace policy or archival context, it should live in
  `bitpod-docs/`.
