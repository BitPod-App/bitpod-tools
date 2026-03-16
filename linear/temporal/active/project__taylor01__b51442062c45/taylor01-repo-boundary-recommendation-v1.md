# Taylor01 Repo Boundary Recommendation v1

Status: Active
Primary issue: [BIT-100 — Define AI-agent portability boundary and repo extraction strategy](https://linear.app/bitpod-app/issue/BIT-100/define-ai-agent-portability-boundary-and-repo-extraction-strategy)
Project: [Taylor01](https://linear.app/bitpod-app/project/taylor01-b51442062c45)

## Current decision

Stay in-repo for now, but make the future extraction boundary explicit immediately.

## Why not extract yet

- Taylor01 is strategically important, but its portable boundaries are still being defined.
- A separate repo right now would force premature moves before the contracts stabilize.
- BitPod remains the proving ground, so keeping implementation nearby reduces coordination cost.

## Why boundary work must start now

- Taylor01 is likely more important than BitPod long-term.
- Future extraction cost will rise quickly if current docs and workflows remain casually BitPod-shaped.
- Portability concerns are allowed to interrupt BitPod work when the alternative is hard lock-in.

## Reserved in-repo landing zones

Future Taylor01-owned content should converge toward:

- `tools/taylor01/core`
- `tools/taylor01/policy`
- `tools/taylor01/adapters`

These directories should exist before major content movement so the target shape is stable.

## Placement rules

### Place in Taylor01 core

- agent contracts
- orchestration logic
- certainty/evidence rules
- portable runtime abstractions

### Place in Taylor01 policy

- CJ/team operating norms
- workspace trust and hygiene policies
- anti-drift and retrospective rules
- generic artifact naming and approval rules

### Place in Taylor01 adapters

- GitHub, Linear, Discord adapter contracts
- future Slack/Jira interface stubs
- portability checks for ticket/PR workflows

### Keep outside Taylor01 subtree

- BitPod product canon
- BitPod brand assets
- BitPod domain semantics
- BitPod app roadmap and user-facing contracts

## Future extraction triggers

Separate repo extraction becomes justified when two or more of the following are true:

- there is a real non-BitPod client or product using Taylor01
- the `tools/taylor01/*` subtree has stable contracts and meaningful content
- adapter work for Slack/Jira or other orgs is active
- cross-product changes are being blocked by BitPod repo coupling
- the cost of staying in-repo exceeds the cost of a split

## Current recommendation

- no separate repo yet
- explicit boundary now
- portable-by-default classification for new reusable artifacts
- controlled temporary bypass allowed when portability work is not yet worth the interruption
- documented coupling log for anything still mixed
