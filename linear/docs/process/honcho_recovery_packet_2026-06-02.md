# Honcho Recovery Packet — canonical identity, hydration, and ticket correction

Status: active recovery packet
Date: 2026-06-02
Scope: Taylor01/Hermes/Honcho memory routing, hydration gates, and Linear correction guidance
Source drafts consolidated from untracked files dated 2026-05-29:

- `hydration_recovery_plan_2026-05-29.md`
- `routing_patch_honcho_canonical_identity_2026-05-29.md`
- `stale_ticket_audit_honcho_memory_2026-05-29.md`

This packet preserves only findings that are still actionable or still useful as guardrails. It intentionally does not preserve bearer-token-looking examples, stale localhost/API values, obsolete workspace names, or old apply-now steps that are already reflected in the current local profile.

## Verification snapshot used for this packet

Verified in the current `bitpod-tools` working tree on 2026-06-02:

- Current repo path: `/Users/taylor01/BitPod-App/bitpod-tools`.
- Current branch: `codex/hermes-first-migration-gate`.
- Current Taylor01 Honcho config path inspected: `$HOME/.hermes/profiles/taylor01/honcho.json`.
- The current `hermes.taylor01` host has `pinPeerName: true`.
- The current `hermes.taylor01` host uses workspace `bitpod-t01`, human peer `cj`, and AI peer `taylor`.
- The current `hermes.taylor01` host aliases both `CJ` and `1722576402` to `cj`.
- Current session mappings reported by `hermes -p taylor01 honcho sessions` include:
  - `/Users/taylor01/BitPod-App` → `bitpod-app`
  - `/Users/taylor01/BitPod-App/bitpod-tools` → `bitpod-tools`
  - `/Users/taylor01/BitPod-App/taylor01-mind` → `taylor01-mind`
  - `/Users/taylor01/BitPod-App/taylor01-runtime` → `taylor01-runtime`
  - `/Users/taylor01/BitPod-App/taylor01-mind/apps/t01-agent` → `t01-agent`
  - `/Users/taylor01/BitPod-App/taylor01-mind/src/taylor01_skills/skills/pm_acceptance_testing` → `pm-acceptance-bit-537`

Not verified by this packet:

- Live Honcho cloud contents for any historical orphan conclusions.
- Current Linear status/field values for the tickets named below.
- A live Telegram → Hermes Taylor01 → Codex heartbeat.

## Still-live recovery findings

### 1. Canonical human peer identity must stay pinned

The old draft correctly identified a high-risk class of failure: Telegram runtime identity values, such as numeric chat/user IDs, must not become the durable Honcho human peer for Taylor01.

Current local truth shows the direct `add pinPeerName` step is no longer an open task for the inspected Taylor01 profile: `pinPeerName: true` is already present, and `1722576402` aliases to `cj`.

Operating rule:

- Do not remove `pinPeerName: true` from the Taylor01 Honcho profile.
- Do not treat a numeric Telegram ID as the canonical human identity.
- Do not claim this issue is solved by older broker/admin-key work unless the claim includes post-routing evidence for peer identity.

### 2. Session routing remains a guardrail, not the source of identity truth

The old draft correctly identified session-name sprawl as a reliability risk. Current local truth shows the active repo cwds now map to stable names, including `bitpod-tools`.

Operating rule:

- Stable cwd-to-session mappings should exist for active Taylor01 repos and special-purpose skill lanes.
- Session names are routing containers, not proof of memory ownership.
- Legacy or recovery names such as `pm-teaching`, `pm-learning`, `/topic`, `/session`, `/new`, or `/status` must not be treated as product intent or canonical PM context.
- Telegram DM session names may remain platform-shaped until a real Hermes config override exists; canonical peer attribution is the safety-critical part.

### 3. Historical numeric-peer conclusions require audit before migration

The peer fix and aliases protect future writes, but they do not prove historical conclusions under a numeric peer were migrated or are worth migrating.

Operating rule:

- Do not bulk-migrate old Honcho conclusions.
- First list the historical conclusions, then classify each as durable rule/preference, ephemeral session fact, or already captured elsewhere.
- Re-ingest only durable rules/preferences under the canonical `cj` peer.
- Discard ephemeral or duplicate facts.
- Never paste bearer tokens or auth headers into tracked process docs.

### 4. BIT-527 hydration remains a PM-acceptance prerequisite unless explicitly re-verified or waived

The old hydration draft correctly preserved a gate: PM acceptance work should not rely on a memory packet that was supposedly accepted but never ingested.

Current local truth shows there is now a stable `pm-acceptance-bit-537` session mapping, but this packet did not verify that BIT-527 Memory Packet v1.0 was ingested into Honcho.

Operating rule:

- Before using Taylor01 PM acceptance as a strong gate for BIT-537-family work, verify one of:
  - BIT-527 Memory Packet v1.0 was ingested into Honcho under the canonical `cj` peer, or
  - CJ explicitly waived that prerequisite for the specific acceptance run.
- If the gate is missing, PM acceptance outputs from that period should be rechecked rather than treated as final.

### 5. Process-doc hydration must stay narrow

The old hydration draft correctly warned against bulk-importing `linear/docs/process/` into Honcho. The archive is mixed current/stale/superseded material.

Operating rule:

- Do not bulk-hydrate process docs into Honcho.
- Promote only active policy clauses from active docs.
- Use `memory_stewardship_service_contract_v1.md` when durable memory mutation is needed: proposal first, approval before write, contradiction scan when guidance conflicts.

High-confidence docs to reference before memory promotion:

- `linear_operating_guide_v3.md`
- `linear_issue_template_evidence_contract_v2.md`
- `hermes_first_closure_migration_gate_v1.md`
- `memory_stewardship_service_contract_v1.md`
- `vera_qa_lane_contract_v1.md`

### 6. Cross-agent Honcho write assumptions need current-profile proof

The old ticket audit said some non-Taylor agents were silently failing due to missing gateway/base URL config. That exact detail is stale for the current inspected profile shape, but the still-live finding is broader: do not assume an agent writes to Honcho unless its active profile is enabled and observable.

Current local Taylor01 Honcho config shows `hermes.mara`, `hermes.nora`, `hermes.simon`, and `hermes.vera` are present but disabled. No `shiva` host entry was observed in the inspected config.

Operating rule:

- A ticket should not claim cross-agent shared Honcho memory is working merely because shared memory was planned or a host key exists.
- Require current enabled-profile evidence and a successful write/recall check before claiming a non-Taylor agent participates in Honcho memory.

## Linear tickets and assumptions that need correction or re-check

This table is a correction guide. It does not claim current Linear field values were live-queried on 2026-06-02.

| Item | Correction needed | Action |
|---|---|---|
| BIT-523 | Broker/admin-key repair was real, but it is not by itself proof that Telegram peer identity was canonicalized. | Leave core auth-fix claims alone; avoid expanding the ticket into peer-identity proof unless routing evidence is attached. |
| BIT-524 | Master-plan memory hydration did not cover the later-discovered Telegram peer identity fragmentation. | If the ticket text implies complete Honcho memory health, add a correction or link to this packet / later routing work. |
| BIT-525 | Hydration from sessions may be incomplete if conclusions landed under a numeric peer. | Re-check peer IDs for any conclusions before treating them as canonical Taylor01 memory. |
| BIT-527 | Accepted/completed status is suspect if Memory Packet v1.0 was not actually ingested into Honcho. | Verify ingestion evidence or add a correction that acceptance did not complete the Honcho ingest deliverable. |
| BIT-537 | PM acceptance work is unsafe if it depends on the missing BIT-527 memory packet. | Gate PM acceptance on verified BIT-527 ingestion or explicit CJ waiver; re-review acceptance runs made before the gate. |
| BIT-542 | Memory-budget rebalancing should not proceed from outage-era assumptions. | Run only after route health and hydration prerequisites are verified. |
| BIT-506 | Shared cross-agent memory should not be marked achieved through Honcho unless active agent profiles are enabled and write checks pass. | Correct any claim that disabled or unobserved non-Taylor profiles are successfully writing to Honcho. |
| BIT-489 | Earlier hydration-diff evidence predates the peer-identity finding. | Treat as partial discovery unless rerun against canonical peer/session routing. |
| BIT-91 | OpenClaw-era governance/memory/eval scope is stale relative to Hermes-first architecture. | Refresh or narrow before pickup; do not revive OpenClaw as a runtime fallback. |
| “pm-learning” | The old draft found no real `pm-learning` session, and current deterministic routing treats `pm-learning` as recovery/noise, not product intent. | Remove or correct assumptions that depend on a canonical `pm-learning` session. |
| New-ticket suggestions from the 2026-05-29 drafts | Some may now be duplicate or partially satisfied by later routing work. | Check current Linear and later routing tickets before creating duplicates. |

## Packet use in future work

Use this packet when work touches:

- Taylor01/Hermes/Honcho identity routing.
- PM acceptance memory prerequisites.
- Honcho hydration or orphan conclusion migration.
- Linear ticket cleanup where older tickets overclaim memory health.
- Any process-doc-to-memory promotion.

Do not use this packet as proof of:

- live Linear ticket state,
- live Honcho cloud contents,
- live Telegram heartbeat success,
- or current non-Taylor agent memory writes.
