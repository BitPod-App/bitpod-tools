# Hermes-First Closure and Clean Home Migration Gate v1

Status: active decision gate
Date: 2026-05-13
Primary Linear issue: [BIT-472 — Fresh Hermes clean-room onboarding proof with CJ-owned OAuth](https://linear.app/bitpod-app/issue/BIT-472/fresh-hermes-clean-room-onboarding-proof-with-cj-owned-oauth)
Related: [BIT-427 — Plan: Decide Taylor01/Hermes/Vera runtime, subscription, and auth path](https://linear.app/bitpod-app/issue/BIT-427/plan-decide-taylor01hermesvera-runtime-subscription-and-auth-path), [BIT-382 — Plan: Archive old OpenClaw residue only; abandon reinstall path](https://linear.app/bitpod-app/issue/BIT-382/plan-archive-old-openclaw-residue-only-abandon-reinstall-path)

## Decision

BitPod/Taylor01 work should move to a Hermes-first operating model.

OpenClaw is not a fallback, alternative runtime, or retained execution arm. It remains only historical context and closure/cleanup scope. Any active docs or tickets that imply OpenClaw can be revived as the Taylor01 runtime should be updated, canceled, or narrowed to cleanup only.

## Current verified local shape

Two Hermes homes were found on the Mini-side Taylor01 account:

- `$HOME/.hermes` — currently the plain `hermes` command home; weaker/stale shape with a generic default SOUL and a Vera profile.
- `$HOME/.hermes-bit472` — ticket-shaped temporary home with the useful proof-era shape: default Hermes, `taylor01`, and `vera` profiles, plus OpenAI Codex OAuth evidence.

The canonical target is `$HOME/.hermes`. The `-bit472` home must not remain the long-term active home because ticket-shaped root state becomes harder to unwind over time.

## Target agent model

Keep the three-role Hermes shape after migration:

- `default` / Hermes: neutral internal ops, routing, paper trail, and dashboard-side coordination.
- `taylor01`: PM/chief-of-staff/orchestration support for CJ and BitPod workflows; not the default coding executor.
- `vera`: QA/release-integrity agent, used for evidence-backed PR/issue review and QA gate unblocking.

Taylor01 may organize, synthesize, create handoff packets, and coordinate Kanban/Linear/GitHub surfaces. Codex remains the main coding executor unless later evidence justifies a different role.

Vera must preserve exact verdicts: `PASSED`, `FAILED`, `NO_VERDICT`. Vera must not approve without evidence, invent test results, or use Taylor identity/secrets.

## Migration gate

Stop before hydration and choose exactly one path.

### Option A — CJ fresh install, Codex hydrates later

Recommended.

CJ creates a clean official Hermes install at `$HOME/.hermes`. Codex later compares the fresh install with `$HOME/.hermes-bit472` and proposes a hydration diff before copying SOULs, profiles, skills, config, dashboard references, or auth-adjacent state.

CJ steps, exact order:

```bash
# 1. Confirm you are on the Mini user account you intend to use
hostname
whoami
echo "$HOME"

# 2. Make a timestamp
TS="$(date +%Y%m%d-%H%M%S)"

# 3. Create non-destructive backups; do not delete anything
mkdir -p "$HOME/hermes-migration-backups/$TS"
cp -a "$HOME/.hermes" "$HOME/hermes-migration-backups/$TS/.hermes.preexisting" 2>/dev/null || true
cp -a "$HOME/.hermes-bit472" "$HOME/hermes-migration-backups/$TS/.hermes-bit472.source" 2>/dev/null || true

# 4. Move the current weak/default .hermes out of the canonical path
mv "$HOME/.hermes" "$HOME/.hermes.pre-fresh-$TS"

# 5. Install Hermes officially into $HOME/.hermes
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash

# 6. Reload zsh path
source "$HOME/.zshrc"

# 7. Verify clean install
command -v hermes
hermes --version
hermes status

# 8. Run official setup/model flow and select OpenAI Codex OAuth/provider
hermes setup

# 9. Verify provider-backed baseline
hermes status
hermes profile list
```

CJ stops there. Codex then proposes hydration from `$HOME/.hermes-bit472`; it does not silently copy auth caches, tokens, exact secret references, or machine-local launch state.

### Option B — Codex full migration

Codex snapshots both homes, promotes `$HOME/.hermes-bit472` into `$HOME/.hermes`, rewrites hardcoded `-bit472` paths, updates wrappers/proxies/launchd/Tailscale references, and validates profiles/dashboard/auth.

This is faster but riskier. It requires explicit CJ approval before execution.

## Vera QA gate

Vera should be the explicit non-author QA/PR review route when GitHub or process rules block a PR author from reviewing their own PR.

A Vera review should declare its mode:

- Blocker review: shallow check used only to unblock a formal QA gate when the change is small and low risk.
- Standard review: review of diff, linked issue, tests, and acceptance criteria.
- Deep review: stronger model/reasoning/tool use for high-risk code, security-sensitive changes, broad refactors, migrations, runtime/auth/secrets work, or CJ-requested scrutiny.

Vera may recommend using additional review surfaces such as Codex code review, but the Vera verdict must remain her own evidence-backed verdict and must not be replaced by a managed review product.

## Identity and attribution policy

Technical agent health does not require every Hermes agent to have a separate GitHub or Linear user. What matters first is separate profile state, SOUL, skills, memory/session state, runtime credentials, and provenance.

GitHub identity becomes practically necessary when platform review gates require a reviewer distinct from the PR author. A Vera GitHub identity is justified if it is needed for real PR review gates.

A separate Linear seat is not required for v1. Use the existing CJ/Taylor01 Linear identities plus explicit signatures such as:

`[agent: Vera][skill: PR QA Review][runtime: Hermes]`

Keep API keys, service accounts, and provider credentials separated by runtime role where those credentials spend money, mutate platforms, or carry review authority.

## BIT-413 handling

Do not mark [BIT-413 — Cost dashboard and prompt-template control surface MVP](https://linear.app/bitpod-app/issue/BIT-413/cost-dashboard-and-prompt-template-control-surface-mvp) Done merely because Hermes is useful.

If the cost-dashboard/prompt-control umbrella is too broad, split or cancel stale scope truthfully. Cost visibility remains useful, but it is not required as proof that Hermes-first is the direction.


## Honcho recovery packet

Honcho identity, session-routing, hydration, and stale-ticket correction guidance is tracked in `honcho_recovery_packet_2026-06-02.md`.

Use that packet before claiming Taylor01/Honcho memory health, running PM-acceptance gates that depend on BIT-527 hydration, migrating orphan conclusions, or correcting older Linear tickets. The packet supersedes raw 2026-05-29 recovery drafts and intentionally omits token-like examples and stale apply-now values.

## Executable route preflight

The Telegram -> Hermes Agent Taylor01 -> Codex migration gate is no longer document-only in `bitpod-tools`. The repo-backed executable preflight is:

```bash
python3 tools/taylor01/adapters/hermes/telegram_taylor01_codex_gate.py
```

This preflight is intentionally read-only. It may return `BLOCKED` without indicating a regression; `BLOCKED` means at least one prerequisite is not currently observable from the local environment. A `PASS` means only that the local prerequisites are present enough to proceed to a live Telegram heartbeat test; it does not prove a Telegram message was received, a Hermes Taylor01 task responded, or Codex executed work.

The preflight preserves the OpenClaw boundary by failing closed if active OpenClaw runtime environment variables are present. OpenClaw remains historical closure context only, not a fallback route.

## Acceptance

- Plain `hermes profile list` from `$HOME/.hermes` shows `default`, `taylor01`, and `vera` after hydration.
- No active config, SOUL, wrapper, proxy, launchd, or Tailscale reference points at `$HOME/.hermes-bit472` after migration.
- OpenAI Codex OAuth/provider status works from canonical `$HOME/.hermes` without publishing secrets.
- Hermes dashboard starts from canonical `$HOME/.hermes` and remains localhost/Tailnet-scoped, not public Funnel.
- Taylor01 and Vera both pass public-safe smoke tests.
- Vera can produce evidence-backed PR review verdicts with `PASSED`, `FAILED`, or `NO_VERDICT`.
- Linear/docs no longer present OpenClaw as a fallback or alternative runtime.

## Official references

- [Hermes Installation](https://hermes-agent.nousresearch.com/docs/getting-started/installation/)
- [Hermes Quickstart](https://hermes-agent.nousresearch.com/docs/getting-started/quickstart/)
- [Hermes Profiles](https://hermes-agent.nousresearch.com/docs/user-guide/profiles)
- [Hermes SOUL.md](https://hermes-agent.nousresearch.com/docs/user-guide/features/personality)
