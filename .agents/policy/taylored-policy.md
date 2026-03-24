<!-- GENERATED FILE. DO NOT EDIT HERE. -->
<!-- CANONICAL SOURCE: bitpod-docs/process/taylored-policy.md -->
<!-- MIRROR ROLE: repo packet mirror -->
# Taylored Work Policy

CANONICAL SOURCE: `bitpod-docs/process/taylored-policy.md`
LOCAL ROOT MIRROR: `$WORKSPACE/taylored-policy.md` bootstrap mirror only
EDIT SURFACE: edit this file first; generated mirrors must not become parallel canon

NAME: Taylored Work Policy
STATUS: Active
DATE: 2026-03-24
VERSION: 2.0
OWNER: Workspace / Product Development
DESCRIPTION: Canonical repo-backed global work-policy contract for local umbrella bootstrap and cloud-visible repo distribution.
SCOPE: Workspace-wide authority, portability, and artifact governance.
ENTRYPOINT: repo-root `AGENTS.md` files and generated bootstrap mirrors.
DEPENDENCIES: `AGENTS.md`, `taylored-policy-rules.md`, shared process docs.
OVERRIDE_POLICY: Repo `AGENTS.md` may declare explicit rule exceptions listed in the registry.

STATUS:

- active
- canonical repo-backed global work-policy contract
- machine-first
- prohibition-first
- public-safe

TOKENS:

- `#WORKSPACE_ROOT` = deployed product/workspace root
- `#LOCAL_WORKSPACE` = local-only operating workspace under the root
- `#CODEX_HOME` = machine-local Codex state home
- `#PRODUCT_OWNER` = top product authority role for the deployed workspace
- `#TEAM_OWNER` = top team authority role for the deployed workspace
- `#PM` = product-management authority role

CANONICAL POLICY SURFACES:

- `bitpod-docs/AGENTS.md` = canonical repo-backed policy entrypoint
- `bitpod-docs/process/taylored-policy.md` = canonical global work-policy contract
- `bitpod-docs/process/taylored-policy-rules.md` = canonical prohibition list

COMPATIBILITY SURFACES:

- `$WORKSPACE/AGENTS.md` = local umbrella bootstrap mirror only
- `$WORKSPACE/taylored-policy.md` = local umbrella bootstrap mirror only
- `$WORKSPACE/taylored-policy-rules.md` = local umbrella bootstrap mirror only

FALLBACK FILE NAMES:

- lowercase `agents.md` may exist as a compatibility fallback only
- lowercase files are never canonical when uppercase files exist

DEFAULT MODEL:

- everything is permitted unless explicitly prohibited by the root policy rules
- repo `AGENTS.md` adds instructions only
- repo `AGENTS.md` may declare explicit rule exceptions only when the root policy rules allow them
- exception behavior must never be silent

DISCOVERY MODEL:

- local umbrella bootstrap may start from `$WORKSPACE/AGENTS.md`
- cloud and repo-local Codex runs must discover policy from files that exist inside the actual repo
- do not rely on umbrella-root-only files for cloud-visible behavior

READ ORDER:

1. repo-root `AGENTS.md` in the active repo
2. local packet or canonical policy files referenced by that repo-root `AGENTS.md`
3. repo-specific nested `AGENTS.md` or `AGENTS.override.md`, if present
4. task-specific canonical docs explicitly pointed to by the active instruction chain

AUTHORITY MAP:

- repo-root `AGENTS.md` = active runtime entry routing inside each repo
- `bitpod-docs/process/taylored-policy.md` = global guardrails and authority model
- `bitpod-docs/process/taylored-policy-rules.md` = prohibition IDs, enforcement state, alertability, and exception eligibility
- repo `AGENTS.md` = repo-specific execution instructions, workflow guidance, model defaults, and canonical doc pointers
- repo `README.md` = orientation and navigation only
- shared process docs = detailed semantics, naming, lifecycle, audit behavior, and packet contracts

WORKFLOW POINTER:

- for cross-repo Linear issue-update semantics, treat `update Linear` as `make the issue materially more truthful`
- that default preserves existing assignee/delegate by default and does not include assigning/delegating issues to Codex or mentioning `@Codex`; those actions are explicit cloud-task delegation only
- the canonical detailed rule surface for that behavior is `$WORKSPACE/bitpod-tools/linear/docs/process/linear_operating_guide_v3.md`

ROLES:

- `PRODUCT_OWNER`
- `TEAM_OWNER`
- `PM`
- `HUMAN_MEMBER`
- `AI_AGENT`

EXCEPTION MODEL:

- repo `AGENTS.md` may declare an explicit exception to a root prohibition
- every override must reference exact rule IDs from the root policy rules
- every exception must state scope, reason, conditions, owner role, and whether it is temporary or standing
- an exception may add permissions only within the scope and conditions it declares
- if a rule is marked non-exception-eligible in the root policy rules, no repo file may bypass it

ROOT VS REPO SPLIT:

KEEP IN GLOBAL POLICY CANON:

- authority and precedence
- workspace and machine-profile rules
- portability boundaries
- root/local lifecycle guardrails
- the structure that governs how the root policy rules are applied
- packet and mirror discipline for cloud-visible repo distribution

KEEP IN REPO `AGENTS.md`:

- task routing inside the repo
- preferred agent-role guidance
- model/task defaults
- repo-specific workflow instructions
- pointers to repo docs and README

KEEP OUT OF GLOBAL POLICY CANON:

- repo product behavior
- repo runtime behavior
- repo feature implementation detail
- repo-specific artifact contracts

LOCAL WORKSPACE DOC SURFACE RULE:

- `#LOCAL_WORKSPACE` is not a documentation surface
- agents and humans must not create `README.md` or equivalent local folder guidance files inside `#LOCAL_WORKSPACE`
- local folder behavior must be governed by canonical policy docs, not by ad hoc local readmes
- any exception must be explicit, scoped, and traceable through the root policy-rule system

PROFILES:

PUBLIC GLOBAL CANON MAY INCLUDE:

- lightweight setup model
- generic local workspace model
- tokenized path guidance
- generic owner/role model
- existence of fuller human setup surfaces

PUBLIC GLOBAL CANON MUST NOT INCLUDE:

- person-specific local paths
- person-branded folder names as canonical public identifiers
- private break-glass setup detail
- private human-only operating instructions

MACHINE STATE:

- primary machine-local Codex state lives in `#CODEX_HOME`
- checked-in `.codex/` may hold compatibility pointers and shared project-scoped metadata only
- checked-in `.codex/` must not be the primary machine-state home

SECRETS:

- no secrets in tracked repo files
- no secrets in shared handoff folders by default
- no repo-local `.env` files as the primary runtime secret mechanism
- runtime secret access must come from machine-local secure injection or an approved external secret store

PORTABILITY:

- Taylor01 portability should rely primarily on repo-root `AGENTS.md`, `bitpod-docs/process/taylored-policy.md`, `bitpod-docs/process/taylored-policy-rules.md`, and shared canonical docs
- GitHub-native files are used only for GitHub-native behavior
- `.github` repo may hold governance docs or automation, but it is not the sole runtime instruction source

PACKET AND MIRROR RULE:

- canonical policy is edited in `bitpod-docs`
- distributed repo packets and local root bootstrap files are generated from canon
- mirrored files must declare canonical source and `DO NOT EDIT HERE`
- generated runtime packets must not become silent parallel canon

ROOT REFERENCES:

- `$WORKSPACE/bitpod-docs/process/taylored-policy-rules.md`
- `$WORKSPACE/bitpod-docs/process/read-first-protocol.md`
- `$WORKSPACE/bitpod-docs/process/truthfulness-and-verification-policy.md`
- `$WORKSPACE/bitpod-docs/process/codex-global-policy-packet-contract.md`

TRUTHFULNESS DISCLOSURE RULE:

- if data, context, memory, or other information was lost, the loss must be stated directly when relevant or when asked
- if the reason for the loss is known, the known reason must be stated directly rather than replaced with a merely plausible alternative
- do not use euphemisms, hedges, or softer terminology to avoid saying the agent lied, is lying, omitted material truth, or misled the operator
- when truth is lie, use `I` plus `lie/lied/lying` directly
- when truth is omission, use `I lied by omission`, not `omitted` by itself
