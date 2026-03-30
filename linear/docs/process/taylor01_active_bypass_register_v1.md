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
| T01-B01 | `linear/docs/process/linear_operating_model_v1.md` + `linear/docs/process/linear_operating_guide_v3.md` | Active BitPod-specific Linear doctrine is still needed for current org execution and would be premature to normalize into Taylor core or a generic adapter contract right now | Revisit when active Taylor01 / Claw runtime and operator-surface decisions stabilize enough to define a real portable adapter shape | Keep local now; document boundary explicitly and avoid silent platform assumptions |
| T01-B02 | `/Users/cjarguello/bitpod-app/local-workspace/local-codex/skills/**/*.md` and similar SKILL.md-based local operator surfaces | Current local skill surfaces are useful operator overlays, but they are not yet a trustworthy definition of the long-term Taylor capability model | Revisit after the active Taylor01 / Claw runtime lane defines the real operator/capability surface more concretely | Keep local now; treat as transitional and do not extract broadly |
