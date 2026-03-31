# Taylor01 Current Artifact Durability Map v1

Status: Working baseline
Primary issue: [BIT-100 — Define AI-agent portability boundary and repo extraction strategy](https://linear.app/bitpod-app/issue/BIT-100/define-ai-agent-portability-boundary-and-repo-extraction-strategy)
Related issues:
- [BIT-198 — Plan: Taylor01 runtime boundary and Claw-direction architecture](https://linear.app/bitpod-app/issue/BIT-198/plan-taylor01-runtime-boundary-and-claw-direction-architecture)
- [BIT-205 — Define Taylor01 operator intake and supporting surface adapters](https://linear.app/bitpod-app/issue/BIT-205/define-taylor01-operator-intake-and-supporting-surface-adapters)

## Purpose

Classify the current highest-signal Taylor-related artifacts across the active
repos so durable substrate, transitional compatibility, and BitPod/local
overlays stop being treated as one blended bucket.

This is intentionally curated rather than exhaustive.

## Classification map

| Repo / area | Current role | Classification | Why |
| --- | --- | --- | --- |
| `taylor01-skills` service/auth/truthfulness/provenance substrate | portable Taylor substrate | durable substrate | this repo already owns generic service, auth, truthfulness, provenance, and capability-package substrate rather than BitPod-local doctrine |
| `taylor01-skills` current packaged `SKILL.md` installs | compatibility distribution path | transitional compatibility | useful current install surface, but current canon explicitly avoids treating `SKILL.md` as the final container |
| `bitpod-taylor-runtime` launcher-backed Mini runtime | live embodiment lane | durable substrate for current phase | this is the current real execution substrate for Taylor on the Mini |
| `bitpod-taylor-runtime` current transport/runtime packaging details | current implementation shape | transitional compatibility | current runtime is real, but its exact packaging should not be mistaken for final Claw shape |
| `bitpod-tools` active Linear doctrine and guides | BitPod operating truth | BitPod/local overlay | these are the truthful owning doctrine surfaces for the current BitPod lane |
| `bitpod-tools` OpenClaw operator contract | current operator truth | BitPod/local overlay with future portable potential | active current truth lives here, but the artifact is still tied to the BitPod proving-ground lane |
| `bitpod-tools` portability boundary docs (`taylor01_*`) | boundary and extraction framing | transitional compatibility | these are important and durable in intent, but many still exist as in-repo staging doctrine rather than final extracted Taylor core |
| local `SKILL.md` operator surfaces around the BitPod lane | live local operators | transitional compatibility | useful and real today, but still local overlays rather than durable Taylor identity |

## Top transitional artifacts that should not harden further

- current `SKILL.md`-based operator surfaces
- current OpenClaw-over-Taylor-runtime layering
- Taylor-related portability scaffolding still living in `bitpod-tools`
- current runtime packaging details in `bitpod-taylor-runtime` beyond the
  launcher-backed embodiment floor

## BitPod overlays that should remain local for now

- active Linear doctrine and guide surfaces
- checkpoints, closeout packs, and issue-facing execution overlays
- current OpenClaw operator-contract truth as long as the proving ground is
  still BitPod-local

## Working interpretation

- `taylor01-skills` is the strongest current center for portable substrate.
- `bitpod-taylor-runtime` is the current real embodiment lane.
- `bitpod-tools` is still the truthful owner of active BitPod/OpenClaw doctrine.
- local overlays should remain visible, but should not keep accumulating as if
  they were durable Taylor platform shape.
