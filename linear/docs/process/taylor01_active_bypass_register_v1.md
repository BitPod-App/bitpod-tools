# Taylor01 Active Bypass Register v1

Status: Active
Primary issue: [BIT-100 — Define AI-agent portability boundary and repo extraction strategy](https://linear.app/bitpod-app/issue/BIT-100/define-ai-agent-portability-boundary-and-repo-extraction-strategy)
Project: [Taylor01](https://linear.app/bitpod-app/project/taylor01-b51442062c45)

## Purpose

Track meaningful temporary Taylor01 portability bypasses so they do not disappear into memory or turn into vague long-lived backlog.

Use this register only for active exceptions that should be reviewed soon.

Do not put every tiny shortcut here.

## Review cadence

Review active entries:

- on the next related touch, or
- during the next weekly Taylor01 review,
- whichever comes first

## Exit conditions

Remove an entry when:

- the coupling is resolved now
- the artifact is reclassified as intentionally BitPod-specific
- the bypass is promoted into a dedicated Taylor01 follow-up ticket

## Active entries

| Ref | Area | Reason | Review trigger | Current disposition |
| --- | --- | --- | --- | --- |
| T01-B01 | `linear/docs/process/linear_operating_model_v1.md` + `linear/docs/process/linear_operating_guide_v3.md` | Active Linear doctrine is intentionally kept as a BitPod-specific overlay in the owning repo instead of being extracted into Taylor core or a generic adapter spec now | A real Taylor adapter/core extraction lane is approved, or the current BitPod overlay starts blocking reuse | Keep local as the truthful owning doctrine surface; do not treat this PR as extraction work |
| T01-B02 | Current local `SKILL.md`-based operator surfaces used around the Linear/process lane | Local skill/operator surfaces are useful for current execution but remain transitional overlays rather than the final Taylor capability model | A runtime-backed or otherwise durable Taylor operator surface is defined clearly enough to replace the local overlay truthfully | Keep visible as temporary coupling; do not imply final Taylor embodiment from local skill usage |
