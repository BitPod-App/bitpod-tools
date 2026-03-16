# BIT-29 Command Parity Matrix v1 (Draft)

Date: 2026-03-09
Issue: https://linear.app/bitpod-app/issue/BIT-29/command-parity-zulip-discord-runtime-command-map

## Objective
Map current Zulip runtime command behavior to Discord-compatible equivalents without changing command semantics unexpectedly.

## Proposed parity table (initial)
| Capability | Zulip pattern (current) | Discord target pattern | Notes |
|---|---|---|---|
| Status check | stream/topic trigger | channel command trigger | Keep output format stable |
| Session start | command with context args | slash command with same args | Preserve required params |
| QA summary post | bot posts to stream | bot posts to #40-review-qa | Include linked Linear + PR refs |
| Incident alert | bot mention in stream | bot mention in #60-incidents | Severity prefix retained |
| Memory log append | message/event hook | message/event hook | Route to #70-memory-log |

## Guardrails
- Keep command names stable where possible.
- If command must be renamed, provide alias window and deprecation note.
- Any behavior change must be documented in cutover note.

## Deliverables
- finalized parity matrix
- alias/deprecation list
- smoke commands for pre/post cutover verification
