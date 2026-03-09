# Linear Bot Rules Spec v1 — Codex-ready (label-safe formatting)

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

`🏷️ Type` (required for `☑️ Ready`)
- `⭐️ Feature`
- `🐞 Bug`
- `⚙️ Chore`
- `🎨 Design`
- `🏁 Release`

`🧪 QA` (required in `🧪 In Review`)
- `🔶 QA: Not Done`
- `🔷 QA: Passed`
- `♦️ QA: Failed`

`🔑 PM` (required after `🔷 QA: Passed`)
- `✴️ PM: Waiting`
- `❇️ PM: Approved`
- `❌ PM: Rejected`

`🛑 Blocked` (optional)
- `⛔ needs-discussion`
- `⛔ needs-pm`
- `⛔ needs-specs`
- `⛔ needs-decision`
- `⛔ needs-type`
- `⛔ other`

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

**IF** `🏷️ Type` missing  
→ set `🛑 Blocked = ⛔ needs-type`  
→ comment:  
> “Missing `🏷️ Type`. Set one of: `⭐️ Feature` `🐞 Bug` `⚙️ Chore` `🎨 Design` `🏁 Release`”  
→ move issue → `📂 Backlog`  
→ STOP

**ELSE IF** required headings missing  
→ set `🛑 Blocked = ⛔ needs-specs`  
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
→ move linked Linear issue → `🧪 In Review`  
→ set `🧪 QA = 🔶 QA: Not Done` (overwrite any QA value)  
→ if `🔑 PM` empty: set `🔑 PM = ✴️ PM: Waiting`  
→ comment on Linear issue:  
> “PR in review: <PR_URL>. QA set to Not Done.”

---

### 5.4 On QA result (detected via Linear comment command)

Bot detects QA result from a Linear comment containing either token:
- `QA_RESULT=PASSED`
- `QA_RESULT=FAILED`

Bot also parses `PR_URL=` if present; otherwise use the linked PR.

#### If `QA_RESULT=FAILED`
→ set `🧪 QA = ♦️ QA: Failed`  
→ move issue → `🏗️ In Progress`  
→ comment on PR (as bot):  
> “QA FAILED. Summary: <first 10 lines of QA comment>. See Linear: <issue_url>”  
→ STOP

#### If `QA_RESULT=PASSED`
→ set `🧪 QA = 🔷 QA: Passed`  
→ set `🔑 PM = ✴️ PM: Waiting` (overwrite unless PM already Approved/Rejected)  
→ comment on PR (as bot):  
> “QA PASSED. Awaiting PM approval in Linear. <issue_url>”  
→ STOP

*(If you prefer no tokens, replace this with “QA agent calls bot endpoint with issueId + pass/fail + summary.”)*

---

### 5.5 On PM label change (Linear webhook)

#### If `🔑 PM = ❌ PM: Rejected`
→ move issue → `🏗️ In Progress`  
→ comment on PR (as bot):  
> “PM REJECTED. See Linear for notes: <issue_url>”  
→ STOP

#### If `🔑 PM = ❇️ PM: Approved`
→ comment on PR (as bot):  
> “PM APPROVED. Merge authorized. (Bot will close issue after merge if QA Passed.)”  
→ STOP

---

### 5.6 On GitHub PR merged (linked issue exists)

**IF** `🧪 QA = 🔷 QA: Passed` AND `🔑 PM = ❇️ PM: Approved`  
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

## Amendment (optional v2): enforce `⛔ other` requires comment
Not enforced in v1. For v2:
- On `🛑 Blocked = ⛔ other`, require a new comment within 10 minutes containing:
  - `Blocked reason:`  
  - `Unblock action:`  
Else revert `🛑 Blocked` to `⛔ needs-discussion` and comment: “`⛔ other` requires details.”
