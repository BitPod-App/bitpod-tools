# Linear Operating Guide Changelog

## Active version

- `v3` (effective 2026-03-14)

## Entries

### v3 — 2026-03-14

Reason:
- Merge the still-useful Linear issue hygiene rules from the bootstrap-era best-practices note into the active operating guide.
- Add explicit change-control for high-blast Linear admin/process changes without reviving legacy `M-9` terminology.

Includes:
- issue readiness minimums and small-issue hygiene
- status-truth and explicit-blocker rules
- weekly hygiene guidance
- Linear admin/process change-control and proposal template references

Maintenance update — 2026-03-22:
- define `update Linear` in the active guide as `make the issue materially more truthful`, not merely leave a note
- make field truth maintenance explicit for status/state, links, ownership, project membership, and explicit dependency links
- keep the BIT-35 workflow reconfiguration spec as target behavior while clarifying native-vs-custom automation limits

Maintenance update — 2026-04-15:
- align risky workflow/admin/guidance changes with Control Tower validation and artifact-first completion
- preserve current live workflow names while tightening semantics around `In Review`, `Delivered`, `Accepted`, and `Done`
- make GitHub-driven status changes explicitly fail closed on missing QA, PM, blocker, or release truth
- make `Stale` the primary inactivity-close status and leave `Obsolete` as legacy/edge-case
- align Vera-style QA guidance so it does not overclaim independent embodied QA authority

Maintenance update — 2026-04-28:
- add PR-to-Linear closeout guardrails for merge closeout, retroactive linking, and Linear normalization
- require a mapping table covering PRs, Linear issues, project scope, status class, labels, and bidirectional links
- require single clean retroactive-link comments instead of duplicate or shorthand-only comments
- make project-scope cleanup fail closed when available tooling cannot remove a wrong project assignment

Maintenance update — 2026-05-05:
- add `linear_issue_type_decision_guide_v1.md` as the canonical evidence-based issue-type decision guide
- require issue-type decisions to use evidence rather than title-only inference
- keep `Design` narrow and `Release` rare
- add `linear/contracts/linear_type_classifier_v1.json` as the machine-readable issue-type classifier
- add `linear_type_classifier_corrections_v1.md` as the human correction log that feeds classifier updates/tests
- document the temporary Backlog-status-ID workaround for the observed issue-creation path that can land new Product Development tickets in `Icebox 🧊`

Linked artifacts:
- `/Users/taylor01/BitPod-App/bitpod-tools/linear/docs/process/linear_operating_guide_v3.md`
- `/Users/taylor01/BitPod-App/bitpod-tools/linear/contracts/linear_type_classifier_v1.json`
- `/Users/taylor01/BitPod-App/bitpod-tools/linear/docs/process/linear_issue_type_decision_guide_v1.md`
- `/Users/taylor01/BitPod-App/bitpod-tools/linear/docs/process/linear_type_classifier_corrections_v1.md`
- `/Users/taylor01/BitPod-App/bitpod-tools/linear/docs/process/linear_admin_change_control_v1.md`
- `/Users/taylor01/BitPod-App/bitpod-tools/linear/docs/process/linear_change_proposal_template_v1.md`
- `/Users/taylor01/BitPod-App/bitpod-tools/linear/docs/process/linear_process_v1_1_control_tower_change_proposal_2026-04-15.md`

Rollback target:
- `v2`

### v1 — 2026-03-07

Reason:
- Establish first durable, versioned Linear operating contract for agents.

Includes:
- Evidence-first completion protocol
- Current status model and transition guidance
- Version-to-config mapping for migration Phase 1
- Explicit rollback procedure

Linked artifacts:
- `/Users/taylor01/BitPod-App/bitpod-tools/linear/docs/process/linear_operating_guide_v1.md`
- `/Users/taylor01/BitPod-App/bitpod-tools/linear/docs/process/github_org_baseline_policy_v1.md`
- `/Users/taylor01/BitPod-App/bitpod-tools/linear/docs/process/github_org_baseline_evidence_2026-03-06.md`
- `/Users/taylor01/BitPod-App/bitpod-tools/linear/docs/process/github_org_team_access_map_2026-03-07.md`
- `/Users/taylor01/BitPod-App/bitpod-tools/linear/docs/process/github_repo_security_matrix_2026-03-07.md`
- `/Users/taylor01/BitPod-App/bitpod-tools/linear/docs/process/governance_parity_checklist_2026-03-07.md`

Rollback target:
- This is baseline v1; rollback target is itself until v2 exists.

### v2 — 2026-03-12

Reason:
- Taylor01 is now treated as a co-equal product to BitPod, so relevant Linear execution work requires an explicit portability review gate.

Includes:
- Taylor01 Portability Check requirement for relevant issues
- active evidence contract updated to `linear_issue_template_evidence_contract_v2.md`
- guidance for classifying reusable work as `core`, `policy`, `adapter`, `bitpod-embedding`, or `mixed`

Linked artifacts:
- `/Users/taylor01/BitPod-App/bitpod-tools/linear/docs/process/linear_operating_guide_v2.md`
- `/Users/taylor01/BitPod-App/bitpod-tools/linear/docs/process/linear_issue_template_evidence_contract_v2.md`
- `/Users/taylor01/BitPod-App/bitpod-tools/linear/docs/process/taylor01_portability_review_gate_v1.md`

Rollback target:
- `v1`
