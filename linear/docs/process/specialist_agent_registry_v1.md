# Specialist Agent Registry v1

Status: Working baseline  
Linked issue: [BIT-63 — Specialist agent roster + skills registry v1](https://linear.app/bitpod-app/issue/BIT-63/specialist-agent-roster-skills-registry-v1)

## Registry Rules

- Each specialist has one primary lane and explicit non-goals.
- Skills are versioned and traceable to repository artifacts.
- Delegation should choose the minimal specialist set per task.
- QA lane is independent and cannot self-approve implementation it produced.

## Active Specialist Lanes (v1)

| Specialist lane | Primary mission | Inputs | Outputs | Non-goals |
|---|---|---|---|---|
| Taylor (Orchestrator) | Decompose + dispatch + gate completeness | CJ requests, backlog context | task graph, delegation packets, status transitions | direct implementation ownership |
| Engineering | Build code/infrastructure changes | delegated task packet, acceptance checks | code + tests + validation output | PM prioritization authority |
| QA (Vera contract) | Independent PASS/FAIL verdict | build artifacts, test surface, acceptance criteria | QA verdict + defect evidence | implementing production fixes |
| Design/Brand | UI/brand assets and design system quality | design scope packet, brand constraints | assets/spec updates + provenance notes | infra/runtime ownership |
| Research | Source-grounded analysis and recommendations | question + constraints | citation-backed brief + recommended action | release gating authority |
| Browser/Internet Ops | Reproducible web interactions and external checks | target workflow + tool constraints | run artifacts/screenshots/check outputs | product strategy decisions |

## Skill Binding Baseline

Recommended skill-to-lane mapping:

- Taylor lane: `taylor`, `linear`
- Engineering lane: `linear`, `gh-fix-ci`, `cloudflare-deploy`, `chatgpt-apps`
- QA lane: `qa-specialist`
- Design/Brand lane: design-specific artifacts under `/assets/brand/**` + process docs
- Research lane: `notion-research-documentation`, `openai-docs`
- Browser lane: browser/mcp tools with strict artifact capture

## Lane Assignment Heuristics

1. If work changes behavior/code, include Engineering.
2. If work changes release confidence, include QA.
3. If work changes user-facing visuals/content, include Design/Brand.
4. If work is uncertain and source-heavy, include Research.
5. If work depends on external web UI checks, include Browser lane.

## Escalation

- Cross-lane conflict -> Taylor resolves or escalates to CJ.
- Security/identity risk -> immediate CJ escalation.
- Missing evidence at handoff -> reject handoff and return to sender.
