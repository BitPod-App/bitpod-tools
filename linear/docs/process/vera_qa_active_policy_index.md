# Vera QA Active Policy Index

**Created:** 2026-05-28  
**Owner:** Taylor01  
**Linked issue:** [BIT-497 — Vera QA policy index — consolidate active vs. legacy docs](https://linear.app/bitpod-app/issue/BIT-497/vera-qa-policy-index-consolidate-active-vs-legacy-docs)

> **Quick answer:** The current Vera QA policy is `vera_qa_lane_contract_v1.md`. Routing is via CODEOWNERS → `@BitPod-App/veraqa-tier-1` (or tier-2 for sector-feeds / bitregime-core). Vera runs as a Hermes agent. Start there.

---

## 1. Active Policy — Live and Enforced Right Now

| File | Status | What it governs |
|---|---|---|
| [`vera_qa_lane_contract_v1.md`](./vera_qa_lane_contract_v1.md) | ✅ Working baseline (PRIMARY) | Full QA lane contract: role boundaries, verdict authority, required artifacts, flow, tiered routing model, independence rules |
| [`veraqa_review_routing_guide_v1.md`](./veraqa_review_routing_guide_v1.md) | ✅ Active guidance | CODEOWNERS routing defaults, tier selection rules, bypass guidance |
| [`github_team_purpose_reviewer_routing_v1.md`](./github_team_purpose_reviewer_routing_v1.md) | ✅ Active | GitHub team purpose, dynamic tier policy (v2), escalation scoring |
| [`qa_authority_model_v1.md`](./qa_authority_model_v1.md) | ✅ Working baseline | QA independence rules, verdict authority, gate policy |

### Active GitHub teams

| Team | Members | Default use |
|---|---|---|
| `@BitPod-App/veraqa-tier-1` | `vera-qa` only | Baseline QA for most repos |
| `@BitPod-App/veraqa-tier-2` | `vera-qa` only | High-impact: sector-feeds, bitregime-core (always); other repos when R ≥ 4 |
| `@BitPod-App/veraqa-tier-3-audit` | `vera-qa` only | Manual + rare deep audit only — never default |

**Membership rule:** Only `vera-qa` belongs in VeraQA teams. `taylor-01` must not be a member — PM acceptance is separate from code review.

### Active Linear bot

`bitpod-tools/linear/src/engine.py` parses `QA_RESULT=PASSED/FAILED` tokens from Linear comments and applies `qa-passed` / `qa-failed` labels automatically.

> ⚠️ **Discrepancy note:** The lane contract uses `QA_VERDICT: PASSED/FAILED` as the final line format; the Linear bot appears to parse `QA_RESULT=`. Verify which token the bot actually reads before relying on automated label application. See note at bottom.

---

## 2. Paused — Built But Not Currently Active

| What | Status | Why paused | Re-enable condition |
|---|---|---|---|
| CODEOWNERS routing in most repos | ⚠️ **State ambiguous** — see note | Was commented out pending Vera being a real agent (per BIT-497, 2026-05-20); routing guide updated 2026-05-21 says routing is now active | Verify actual CODEOWNERS state per repo before relying on automated routing |

> ⚠️ **CODEOWNERS state note (2026-05-28):** BIT-497 (created 2026-05-20) says CODEOWNERS routing was commented out. `veraqa_review_routing_guide_v1.md` was updated 2026-05-21 and says routing IS active. These may reflect a re-enable that happened between those dates — or the routing guide was updated aspirationally. **Do a live check of CODEOWNERS in each repo before trusting automated routing.**

---

## 3. Superseded / Legacy — Retained for Reference Only

| File | Status | Why kept |
|---|---|---|
| [`vera_qa_lane_operational_proof_v1.md`](./vera_qa_lane_operational_proof_v1.md) | 📚 Retained proof (not active policy) | Historical evidence that the dedicated QA lane passed its initial proof test with verdict `PASS_WITH_LIMITS`. Useful for audit trail. Do not treat as operating policy. |
| [`vera_runtime_behavior_inventory_from_zulip_v1.md`](./vera_runtime_behavior_inventory_from_zulip_v1.md) | 📚 Preservation inventory (not active policy) | Zulip-era QA behavior inventory preserved during migration. Source material for `vera_runtime_minimum_v1.md`. Not active guidance. |

---

## 4. Target Spec / Informational

| File | Status | What it covers |
|---|---|---|
| [`vera_runtime_minimum_v1.md`](./vera_runtime_minimum_v1.md) | 🎯 Working baseline (future target, not current operating policy) | Defines the minimum Vera runtime/agent surface needed to fully replace the transitional `qa-specialist` skill. Describes required output artifacts (`verification_report.md`, `manifest.json`). Not a claim about current behavior. |

---

## 5. Current Vera Implementation Surface

**As of 2026-05-28:**

| Surface | Status |
|---|---|
| Vera as Hermes agent | ✅ Running — 63+ sessions logged under `~/.hermes/profiles/vera/` |
| `qa-specialist` skill (transitional scaffold) | `bitpod-tools/tools/taylor01/core/agents/vera/skills/qa-specialist/` — installed artifact; repo is the source of truth |
| `vera-qa` GitHub identity | Active — member of all VeraQA tier teams |
| Honcho memory | ✅ Restored (Option A broker) — Vera broker at `127.0.0.1:8787` |

**What Vera does NOT own:** product priority, scope reshaping, implementation, merge approval authority, rewriting acceptance criteria after work is complete.

**Linear bot label path:** `QA_RESULT=PASSED` in a Linear comment → bot applies `qa-passed`. `QA_RESULT=FAILED` → `qa-failed`.

**Required QA artifact:** Every dedicated Vera QA execution must produce a `verification_report.md`-style artifact. Verdict line must be `QA_VERDICT: PASSED`, `QA_VERDICT: FAILED`, or `QA_VERDICT: SKIPPED`.

---

## 6. Re-Enable Checklist for CODEOWNERS Routing

Use this checklist to confirm that CODEOWNERS-based VeraQA routing is active and healthy in any repo:

- [ ] **Check CODEOWNERS file** in the target repo — routing line is present and not commented out (e.g., `* @BitPod-App/veraqa-tier-1`)
- [ ] **Verify team write access** — `@BitPod-App/veraqa-tier-1` (and tier-2 for sector-feeds / bitregime-core) have write access to the repo (GitHub requires this for CODEOWNERS to take effect)
- [ ] **Verify `vera-qa` is active** — confirm `vera-qa` GH account can post reviews and is a member of the VeraQA team on that repo
- [ ] **Confirm branch protection** — `require_code_owner_reviews: true` is set in branch protection for main; `required_approving_review_count: 1`; `dismiss_stale_reviews: true`; `require_last_push_approval: true`
- [ ] **Test with a draft PR** — open a draft PR and confirm VeraQA review is requested automatically from the correct tier team

---

## 7. Notes / Flagged Inconsistencies

The following items look stale or inconsistent across existing docs. **Not silently fixed — flagged here for CJ/Taylor decision.**

1. **QA_VERDICT vs QA_RESULT:** The lane contract specifies `QA_VERDICT: PASSED/FAILED` as the required artifact final line. BIT-497 describes the Linear bot as parsing `QA_RESULT=PASSED/FAILED`. These tokens differ. Verify `bitpod-tools/linear/src/engine.py` and align the contract + bot to use the same token.

2. **CODEOWNERS active/paused state:** As noted above — BIT-497 (2026-05-20) says routing was commented out; routing guide (2026-05-21) says it's active. No single source of truth for live CODEOWNERS state per repo. A live check per repo would resolve this.

3. **BIT-497 says BIT-94 is "unstarted"** — BIT-94 refers to Vera Hermes agent embodiment. Vera is now running as a Hermes agent (BIT-99 is Done). BIT-94 should be checked for whether its ACs are now met or if it tracks something different from BIT-99.

4. **`vera_runtime_minimum_v1.md` references Zulip-era paths** (`/Users/cjarguello/bitpod-app/bitpod-taylor-runtime/...`) that no longer exist. These are legacy input pointers in the "Inputs" section — safe to leave as historical context, but misleading if read as live paths.
