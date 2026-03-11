# Bridge Command Surface Cleanup Spec v1

## Purpose

Clarify the current Bridge command surface so docs match implemented behavior exactly and obsolete ambiguity is removed before later platform migration work.

This is intentionally platform-agnostic cleanup. It does not implement the future transport migration itself.

## Current Truth

There are two different command surfaces in the system today:

1. Bridge CLI/session chat commands in `bitpod-tools/gpt_bridge`
2. Taylor runtime intent/shortcut commands in the Zulip runtime

They are related, but they are not the same surface and should not be documented as if they are interchangeable.

## Canonical Bridge Surface

The implemented Bridge CLI command surface is:

- `~help`
- `~options`
- `~session <prompt>`
- `~sync`
- `~recover`
- `~end`
- `~gpt <message>`
- `~decide <question>`
- `~codex <message>`
- `~cj <message>`
- `~taylor <message>`

Slash aliases that are implemented:

- `/help`
- `/options`
- `/session <prompt>`
- `/sync`
- `/recover`
- `/end`
- `/gpt <message>`
- `/ask <message>`
- `/decide <question>`
- `/codex <message>`
- `/team <message>`

Plain text with no command prefix is routed as a team-chat message.

## Canonical Meaning

- `~session` starts or switches the active session topic/goal
- `~sync` pulls newly logged GPT replies into the local timeline view
- `~recover` attempts recovery of stale/dead/interrupted sessions
- `~end` finalizes the active team chat session
- `~gpt` sends a direct GPT relay inside the team session
- `~decide` is a GPT-routed decision intent
- `~codex`, `~cj`, `~taylor` are direct addressed relays into the shared session

## Non-Bridge Surface

The following belong to Taylor runtime / Zulip Phase 0 semantics, not the Bridge CLI surface:

- topic prefixes:
  - `chat:`
  - `plan:`
  - `decide:`
  - `review:`
- Taylor shortcuts:
  - `!status`
  - `!end`
  - `!intent <chat|plan|decide|review>`
  - `!help`

These should be documented as Taylor transport/runtime commands, not Bridge CLI commands.

## Cleanup Decisions

### Keep

Keep and document clearly:

- `~session`
- `~sync`
- `~recover`
- `~end`
- `~gpt`
- `~decide`
- `~codex`
- `~cj`
- `~taylor`

### Clarify

Clarify that:

- `~decide` remains valid on the Bridge surface
- Taylor `decide:` intent is a separate runtime/topic concept
- Bridge commands and Taylor transport commands are adjacent but not identical

### Do Not Claim

Do not claim the Bridge surface supports commands it does not actually implement.

Do not collapse:

- Bridge relay commands
- Taylor runtime shortcuts
- transport/topic intent semantics

into one fake “universal command list.”

## Documentation Requirements

After cleanup:

- `docs/bridge-runtime-domains.md` must reflect actual Bridge commands
- `gpt_bridge/README.md` must reflect actual Bridge commands
- Taylor runtime docs must remain explicit that `!status`, `!end`, and `!intent` belong to Taylor/Zulip runtime semantics

## Out of Scope

- no removal of commands from code in this pass unless clearly obsolete and unused
- no Discord command redesign in this pass
- no new platform adapter behavior in this pass

## Follow-On

Once this cleanup is merged:

- [BIT-37 — Migrate team session chat commands from Zulip to chosen platform](https://linear.app/bitpod-app/issue/BIT-37/migrate-team-session-chat-commands-from-zulip-to-chosen-platform) can continue against a clearer command/runtime boundary
- later platform migration can decide whether Bridge commands are preserved, adapted, or wrapped by a new transport-facing interface
