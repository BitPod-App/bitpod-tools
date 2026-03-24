# Linear Bot Rules Spec v1 — Codex-ready (label-safe formatting)

Status: historical implementation draft with active reference value, not the final current operating truth

Current live governance still depends on:

- [BIT-79 — Establish interim AI technical QA + CJ acceptance policy](https://linear.app/bitpod-app/issue/BIT-79/establish-interim-ai-technical-qa-cj-acceptance-policy)
- `$WORKSPACE/bitpod-tools/linear/docs/process/interim_ai_technical_qa_cj_acceptance_policy_v1.md`

Use this file as implementation reference, not as a claim that the richer acceptance-state workflow is already live.

Current canonical operating model:

- `$WORKSPACE/bitpod-tools/linear/docs/process/linear_operating_model_v1.md`

This file preserves the older label-safe implementation draft and should not be treated as the active final workflow contract.
The status-first model in `$WORKSPACE/bitpod-tools/linear/docs/process/linear_operating_model_v1.md` supersedes the older `QA Review`, `PM Review`, `Ready`, and `In Acceptance` sections that remain below for historical implementation context.

> **Purpose:** implement a Linear+GitHub automation bot that enforces CJ’s minimal workflow.  
> **Style:** fail-closed; if uncertain, do nothing and comment.

---

## 0) Identity / Attribution (MUST)

### GitHub
- All PR comments + merges MUST be performed by a **GitHub App / bot identity**, not CJ’s PAT.
- If the auth method causes actions to appear as CJ, STOP and report: `AUTH ATTRIBUTION WRONG`.

### Linear
- All Linear mutations MUST run under OAuth **actor=app** (authored by the app).
- If mutations appear as CJ, STOP and report: `LINEAR ACTOR WRONG`.

---

## 1) Data model (exact names)

### 1.1 Statuses

**Unstarted**
- `🧊 Icebox`
- `📂 Backlog`
- `☑️ Ready`

**Started**
- `🏗️ In Progress`
- `🧪 In Review`

**Completed**
- `✅ Done`
- `🪦 Obsolete`
- `🫟 Can't Reproduce`
- `🚫 Canceled`
- `♻️ Duplicate`
- `🗑️ Wont Do`

---

### 1.2 Label Groups (single-select)

`Issue Type` (required for `☑️ Ready`)
- `Type: 📄 Plan`
- `Type: ⭐️ Feature`
- `Type: 🐞 Bug`
- `Type: ⚙️ Chore`
- `Type: 🎨 Design`
- `Type: 🏁 Release`

`QA Review` (required in `🧪 In Review`)
- `🔶 QA: Pending`
- `🔷 QA: Passed`
- `♦️ QA: Failed`
- `◆ QA: Skipped`

`PM Review` (future intended acceptance-stage group; older draft below still mixes it earlier than intended)
- `✴️ PM: Waiting`
- `❇️ PM: Accepted`
- `❌ PM: Rejected`

`Blocked By` (optional)
- `needs-discussion`
- `needs-pm`
- `needs-specs`
- `needs-decision`
- `needs-CTO`
- `needs-type`
- `needs-other`

---

## 2) Required template headings (string match)

Issue description MUST contain these headings (tolerate minor whitespace):

- `Context`
- `Goal`
- `Implementation List`
- `DO NOT list`
- `DoD / Acceptance Criteria`

---

## 3) Linking rule (mandatory)

A PR must reference the Linear issue key (e.g., `ABC-123`) in **PR title OR branch name OR PR body**.

If no link is found, bot MUST do nothing except comment on PR:
> “Missing Linear issue key; cannot automate.”

---

## 4) Event sources

### 4.1 GitHub events
- `pull_request.opened`
- `pull_request.ready_for_review` (or equivalent “in review” signal)
- `pull_request.closed` with `merged=true`

### 4.2 Linear webhooks
- Issue updated (state change)
- Issue labels updated
- Comment created

### 4.3 Scheduled job
- Daily at local midnight (or UTC 00:00): aging scan

---

## 5) Rules (Event → Condition → Actions)

### 5.1 On Linear issue moved to `☑️ Ready`

**IF** `Issue Type` missing
→ set `Blocked By = needs-type`
→ comment:  
> “Missing `Issue Type`. Set one of: `Type: 📄 Plan` `Type: ⭐️ Feature` `Type: 🐞 Bug` `Type: ⚙️ Chore` `Type: 🎨 Design` `Type: 🏁 Release`”
→ move issue → `📂 Backlog`  
→ STOP

**ELSE IF** required headings missing  
→ set `Blocked By = needs-specs`
→ comment:  
> “Missing required sections: Context / Goal / Implementation List / DO NOT list / DoD / Acceptance Criteria”  
→ move issue → `📂 Backlog`  
→ STOP

**ELSE** no action

---

### 5.2 On GitHub PR opened (linked issue exists)
→ move linked Linear issue → `🏗️ In Progress`  
→ comment on Linear issue:  
> “PR opened: <PR_URL>”

---

### 5.3 On GitHub PR enters review (linked issue exists)

Current truth note:

- engineering moves work into `In Review`
- PM labels should not be treated as belonging to `In Review` in the preferred operating model
- the `PM: Waiting` default below is retained as older draft behavior only

→ move linked Linear issue → `🧪 In Review`  
→ set `QA Review = 🔶 QA: Pending` (overwrite any QA value)
→ if `PM Review` empty: set `PM Review = ✴️ PM: Waiting`
→ comment on Linear issue:  
> “PR in review: <PR_URL>. QA set to Pending.”

---

### 5.4 On QA result (detected via Linear comment command)

Bot detects QA result from a Linear comment containing either token:
- `QA_RESULT=PASSED`
- `QA_RESULT=FAILED`

Bot also parses `PR_URL=` if present; otherwise use the linked PR.

#### If `QA_RESULT=FAILED`
→ set `QA Review = ♦️ QA: Failed`
→ move issue → `🏗️ In Progress`  
→ comment on PR (as bot):  
> “QA FAILED. Summary: <first 10 lines of QA comment>. See Linear: <issue_url>”  
→ STOP

#### If `QA_RESULT=PASSED`

Future intended workflow note:

- preferred model is:
  - `QA: Passed` moves `In Review` -> `In Acceptance`
  - `PM: Waiting` / `PM: Accepted` / `PM: Rejected` apply there
- the actions below are the older simpler draft, kept as implementation reference only

→ set `QA Review = 🔷 QA: Passed`
→ set `PM Review = ✴️ PM: Waiting` (overwrite unless PM already Accepted/Rejected)
→ comment on PR (as bot):  
> “QA PASSED. Awaiting PM review in Linear. <issue_url>”
→ STOP

*(If you prefer no tokens, replace this with “QA agent calls bot endpoint with issueId + pass/fail + summary.”)*

---

### 5.5 On PM label change (Linear webhook)

Future intended workflow note:

- PM labels belong to `In Acceptance`, not `In Review`
- `PM: Rejected` should send work back to `In Progress`
- `PM: Accepted` should establish merge readiness
- the concrete actions below remain older draft behavior

#### If `PM Review = ❌ PM: Rejected`
→ move issue → `🏗️ In Progress`  
→ comment on PR (as bot):  
> “PM REJECTED. See Linear for notes: <issue_url>”  
→ STOP

#### If `PM Review = ❇️ PM: Accepted`
→ comment on PR (as bot):  
> “PM ACCEPTED. Merge authorized. (Bot will close issue after merge if QA Passed.)”
→ STOP

---

### 5.6 On GitHub PR merged (linked issue exists)

Current governance note:

- under the temporary BIT-79 path, labels are the authoritative merge gate
- status names like `Accepted` or `In Acceptance` are workflow visibility, not sufficient by themselves for merge authorization
- if the richer acceptance-state model is later implemented, this section should be updated explicitly

**IF** `QA Review = 🔷 QA: Passed` AND `PM Review = ❇️ PM: Accepted`
→ move issue → `✅ Done`  
→ comment on Linear issue:  
> “Merged: <PR_URL> | SHA: <merge_sha>”  
→ STOP

**ELSE** (fail-closed)  
→ comment on Linear issue:  
> “Merged detected but gates not satisfied (need QA Passed + PM Approved). Manual review required.”  
→ STOP

---

## 6) Aging rules (Daily scan; Unstarted only)

Compute `idle_days = now - max(updatedAt, lastCommentAt)`.

### If status = `📂 Backlog` AND idle_days ≥ 30
→ move → `🧊 Icebox`  
→ comment:  
> “Auto-moved to Icebox after 30d inactivity.”

### If status = `🧊 Icebox` AND idle_days ≥ 60
→ move → `🪦 Obsolete`  
→ comment:  
> “Auto-closed as Obsolete after 60d inactivity in Icebox.”

### Never age-out
- `🏗️ In Progress`
- `🧪 In Review`
- any Completed status

---

## 7) Safety / Fail-closed

- If bot cannot confirm linked Linear issue ⇄ PR pairing: do nothing; comment “Linking incomplete.”
- If label names/status names don’t match exactly: do nothing; comment “Config mismatch.”
- If attribution is wrong (actions appear as CJ): do nothing; raise `AUTH ATTRIBUTION WRONG` or `LINEAR ACTOR WRONG`.

---

## Amendment (optional v2): enforce `needs-other` requires comment
Not enforced in v1. For v2:
- On `Blocked By = needs-other`, require a new comment within 10 minutes containing:
  - `Blocked reason:`  
  - `Unblock action:`  
Else revert `Blocked By` to `needs-discussion` and comment: “`needs-other` requires details.”
