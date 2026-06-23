# Vera QA Active Policy Index

**Created:** 2026-05-28  
**Owner:** Taylor01  
**Linked issue:** [BIT-497 — Vera QA policy index — consolidate active vs. legacy docs](https://linear.app/bitpod-app/issue/BIT-497/vera-qa-policy-index-consolidate-active-vs-legacy-docs)

> **Quick answer (updated 2026-06-14 / BIT-617):** The current Vera QA policy is `vera_qa_lane_contract_v1.md`. The active GitHub-native merge gate is the required `vera-qa-gate` check run emitted by the Vera QA Gate GitHub App/bot path. CODEOWNERS / `@BitPod-App/veraqa` review routing is retired as a merge gate because it creates actor/seat ambiguity and blocks the bot-owned QA lane.

---

## 1. Active Policy — Live and Enforced Right Now

| File | Status | What it governs |
|---|---|---|
| [`vera_qa_lane_contract_v1.md`](./vera_qa_lane_contract_v1.md) | ✅ Working baseline (PRIMARY) | Full QA lane contract: role boundaries, verdict authority, required artifacts, flow, single-gate routing model, independence rules |
| [`veraqa_review_routing_guide_v1.md`](./veraqa_review_routing_guide_v1.md) | 📚 Historical / superseded by BIT-617 | Former CODEOWNERS routing model; retained for migration/audit only |
| [`github_team_purpose_reviewer_routing_v1.md`](./github_team_purpose_reviewer_routing_v1.md) | 📚 Historical / superseded by BIT-617 | Former team/CODEOWNERS model; retained for migration/audit only |
| [`qa_authority_model_v1.md`](./qa_authority_model_v1.md) | ✅ Working baseline | QA independence rules, verdict authority, gate policy |

### Active GitHub gate

| Gate | Actor / source | Default use |
|---|---|---|
| `vera-qa-gate` | Vera QA Gate GitHub App / bot-owned result sync | Single required GitHub-native QA check for active repos |

**Retired team route:** `@BitPod-App/veraqa` / the `vera-qa` user seat are not the active merge gate. Keep them only as temporary compatibility surfaces until BIT-619 removes the paid user-seat path. PM acceptance and admin bypass remain separate from QA.

**Superseded routing:** `@BitPod-App/veraqa-tier-1`, `@BitPod-App/veraqa-tier-2`, and `@BitPod-App/veraqa-tier-3-audit` are historical routing concepts only. Vera QA depth is decided by Vera/runtime/process, not by GitHub team name.

### Active Linear bot

`bitpod-tools/linear/src/engine.py` parses `QA_RESULT=PASSED/FAILED` tokens from Linear comments and applies `qa-passed` / `qa-failed` labels automatically.

> ⚠️ **Discrepancy note:** The lane contract uses `QA_VERDICT: PASSED/FAILED` as the final line format; the Linear bot appears to parse `QA_RESULT=`. Verify which token the bot actually reads before relying on automated label application. See note at bottom.

---

## 2. Retired — Do Not Re-enable as Merge Gate

| What | Status | Replacement |
|---|---|---|
| CODEOWNERS routing / `@BitPod-App/veraqa` review requirement | ❌ Retired by BIT-617 direction on 2026-06-14 | Required `vera-qa-gate` check run |

> CODEOWNERS caused attribution ambiguity and a paid `vera-qa` user-seat dependency while not representing the bot/app actor that actually owns the QA result. Do not re-enable CODEOWNERS as the default Vera gate. If a human wants optional review, request it explicitly outside branch protection.

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
| `vera-qa` GitHub identity | Retiring compatibility identity — do not rely on for merge gating; BIT-619 owns seat removal |
| Honcho memory | ✅ Restored (Option A broker) — Vera broker at `127.0.0.1:8787` |

**What Vera does NOT own:** product priority, scope reshaping, implementation, merge approval authority, rewriting acceptance criteria after work is complete.

**Linear bot label path:** `QA_RESULT=PASSED` in a Linear comment → bot applies `qa-passed`. `QA_RESULT=FAILED` → `qa-failed`.

**Required QA artifact:** Every dedicated Vera QA execution must produce `verification_report.md` and `manifest.json`. Verdict/result vocabulary is `PASSED`, `FAILED`, `OVERRIDE`, or `ACTION_REQUIRED`; legacy `SKIPPED` is deprecated/fail-closed.

**CJ QA override V1:** A GitHub-native override may satisfy `vera-qa-gate` for any BitPod repo covered by the GitHub App/webhook, not just this runtime repo. It may pass only when `cjarguello` applies or owns the `QA_OVERRIDE` label (alias `qa-override`) and provides `/qa-override <reason>` in a PR comment or approved PR review for the current head SHA. The sync target in Linear remains `qa-override`. This clears Vera QA only; it is not Vera QA and does not PM-accept the work.

**Expected V2 hardening:** Replace the V1 text/label convention with a stronger GitHub-native bypass path, ruleset audit signal, custom property, or dedicated GitHub Action/App command that must be performed by `cjarguello`.

---

## 6. Vera Gate Checklist

Use this checklist to confirm the custom Vera gate is active and healthy in any repo:

- [ ] Branch protection requires `vera-qa-gate` as a status check.
- [ ] Branch protection does not require CODEOWNERS / PR reviews as the default QA gate.
- [ ] Vera auto-dispatch creates a task for the current PR head SHA.
- [ ] Vera produces `verification_report.md` + `manifest.json`.
- [ ] Result sync updates GitHub `vera-qa-gate` and Linear QA label/status from the Vera result.
- [ ] Every BitPod repo that allows CJ QA override has the GitHub App/webhook installed, subscribes to `issues`, `issue_comment`, and `pull_request_review`, and has label `QA_OVERRIDE` or alias `qa-override`; missing repo setup is a blocker, not an implicit pass.

---

## 7. Notes / Flagged Inconsistencies

The following items look stale or inconsistent across existing docs. **Not silently fixed — flagged here for CJ/Taylor decision.**

1. **QA_VERDICT vs QA_RESULT:** The lane contract specifies `QA_VERDICT: PASSED/FAILED` as the required artifact final line. BIT-497 describes the Linear bot as parsing `QA_RESULT=PASSED/FAILED`. These tokens differ. Verify `bitpod-tools/linear/src/engine.py` and align the contract + bot to use the same token.

2. **CODEOWNERS state:** CODEOWNERS routing is retired as the default Vera gate. Any remaining CODEOWNERS references are historical/migration cleanup targets, not active policy.

3. **BIT-497 says BIT-94 is "unstarted"** — BIT-94 refers to Vera Hermes agent embodiment. Vera is now running as a Hermes agent (BIT-99 is Done). BIT-94 should be checked for whether its ACs are now met or if it tracks something different from BIT-99.

4. **`vera_runtime_minimum_v1.md` references Zulip-era paths** (`/Users/cjarguello/bitpod-app/bitpod-taylor-runtime/...`) that no longer exist. These are legacy input pointers in the "Inputs" section — safe to leave as historical context, but misleading if read as live paths.
