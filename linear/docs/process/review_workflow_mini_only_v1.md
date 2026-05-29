# GPT/Apps/Linear/GitHub Review Workflow — Mini-Only Operating Model v1

Status: Active guidance
Owner: CJ / Taylor01
Related: BIT-417, BIT-401 (Mini-only cockpit hardening)
Last updated: 2026-05-29
Scope: Defines how CJ safely uses GPT, apps, Linear, and GitHub for review/strategy without triggering MacBook-local execution

## Context

The Mini-first operating model means:
- Code **runs** on `mini-01` as `taylor01`
- The MacBook Codex App is the **cockpit** — a UI window into mini-01, not an execution host
- MacBook-local repo work must not reappear through review/strategy app usage

This doc defines the safe MacBook-side review/strategy surface so CJ can continue using GPT, GitHub, Linear, and other apps without eroding the Mini-first boundary.

## Permitted MacBook-Side Review/Strategy Work

### GPT / AI Chat Apps

**Permitted:**
- Strategy brainstorming, planning, and scoping conversations
- Code review and feedback on pasted snippets
- Writing drafts, explanations, or documentation
- Answering questions about tools, APIs, concepts
- Reviewing outputs from Taylor01/Vera/Codex before CJ accepts them

**Not permitted:**
- Running code in GPT's code interpreter / sandbox as a substitute for mini-01 execution
- Using GPT to generate and execute local scripts on MacBook
- Asking GPT to "fix the repo" or make changes that should go through Taylor01

**Boundary check**: Is GPT being used as a thinking/review tool or as a local executor? If thinking/review → fine. If executing → route to Taylor01.

---

### Linear (Issue Management)

**Permitted:**
- Reading, commenting on, and updating issues from MacBook browser or iOS app
- Creating new issues for Taylor01 to work on
- Reviewing Taylor01/Vera's comments and status updates
- Accepting delivered work (`Accepted`, `Done`)
- Adjusting priorities, labels, assignments
- CJ PM workflow fully available from any device

**Not permitted:**
- Creating issues that instruct Taylor01 to modify files that CJ then manually edits in a local MacBook repo

**Boundary check**: Linear is always safe for CJ from any device. No MacBook-local execution is triggered by Linear usage.

---

### GitHub (PR/Issue Review)

**Permitted:**
- Reviewing PRs in GitHub browser — reading diffs, comments, CI status
- Approving or requesting changes on PRs
- Merging PRs after review (safe from browser)
- Filing issues or bug reports
- Viewing Actions/CI results
- Reviewing branch status
- Commenting on commits

**Not permitted:**
- Using GitHub's "Edit file" in-browser editor on files that have active Taylor01 work — this creates conflicts with mini-01's branch state
- Using Codex web/GitHub Copilot on MacBook in local workspace mode as a substitute for the mini-01 cockpit

**Boundary check**: Reading and reviewing GitHub → always safe. Editing files directly in GitHub browser → only safe if Taylor01 is not actively working on the same file in a branch.

---

### Codex App (MacBook Cockpit)

**Permitted:**
- Using the Codex App on MacBook as the UI/cockpit window into `mini-01`
- Sending prompts to Taylor01 via the cockpit (these execute on mini-01)
- Reviewing session output, diffs, and artifacts
- Approving or rejecting Taylor01's proposed actions

**Not permitted:**
- Changing the Codex workspace folder on MacBook to a local repo clone
- Running Terminal commands in the Codex App that target MacBook-local files
- Treating a local MacBook Codex session as equivalent to the mini-01 cockpit

**Boundary check**: Is the Codex App currently configured to connect to mini-01? If yes → cockpit mode, permitted. If it has drifted to local MacBook execution → stop and reconfigure.

---

### Browser / Web Apps (Tailscale Serve)

**Permitted:**
- Accessing `https://mini-01.tail1c36c1.ts.net/` (Hermes Dashboard)
- Accessing `https://mini-01.tail1c36c1.ts.net/prompt` (PCC)
- Accessing `https://mini-01.tail1c36c1.ts.net/access-hub` (Access Hub)
- Any Tailnet-private URL for mini-01 services

**Not permitted:**
- Bookmarking or using old `http://127.0.0.1:PORT/#token=...` OpenClaw URLs (retired)
- Using public/internet-facing URLs for mini-01 services (Tailscale Serve is private by default)

---

### iOS Apps

**Permitted:**
- Linear iOS: full PM workflow
- GitHub iOS: review and comment
- Claude iOS app: conversation and brainstorming (no execution capability)
- Hermes Dashboard via Tailscale on iOS: status monitoring

**Not permitted:**
- iOS Codex app (if ever available) targeting MacBook local repos — same boundary as MacBook Codex

---

## Decision Table

| App/Surface | MacBook-local execution risk | CJ safe to use? | Notes |
| -- | -- | -- | -- |
| GPT chat (Claude.ai, ChatGPT) | None | Yes — as review/strategy | Don't use code interpreter as substitute |
| Linear (browser/iOS) | None | Yes — always | Full PM workflow safe from any device |
| GitHub (browser review) | None | Yes — reading/review/merge | Avoid in-browser file editing during active branches |
| Codex App (mini-01 cockpit) | None if cockpit mode | Yes — in cockpit mode | Verify workspace is pointing to mini-01 |
| Hermes Telegram | None | Yes | Agent-native; no local execution |
| Tailscale mini-01 URLs | None | Yes | Private Tailnet; safe |
| MacBook local Terminal | High | Only for setup/bootstrap | Must not become the execution path |
| MacBook local repo clone | High | Avoid during active mini-01 work | Re-enable only if mini-01 is unavailable |

## Signs of Drift to Watch For

- CJ making file edits in a MacBook-local repo clone while Taylor01 is working on the same branch
- Running `git` commands in MacBook Terminal against a local repo instead of through the Codex cockpit
- Using GitHub's in-browser editor as a shortcut for Taylor01-tracked file changes
- Codex App on MacBook defaulting to a local workspace instead of mini-01

## Recovery When Drift Occurs

1. Check which branch Taylor01 is working on
2. Stash or verify there are no MacBook-local uncommitted changes conflicting with mini-01's branch
3. Re-verify Codex App is pointing to mini-01 workspace
4. Use Taylor01 to reconcile if both sides have edits on the same file
