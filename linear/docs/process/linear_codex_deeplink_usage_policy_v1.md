# Linear Codex Deeplink Usage Policy v1

## Purpose

Define when Linear's Codex deeplink should be used in BitPod's current workflow, and when it should not.

This is intentionally narrow. It does not treat deeplinks as autonomous execution or as a replacement for local workspace verification.

## Current role of deeplinks

Linear deeplinks are useful as a better "open this issue in Codex" entrypoint.

They help with:

- reducing manual copy/paste from Linear into the first Codex prompt
- carrying issue description, comments, references, and attachments into the starting context
- lowering the chance that comment history or linked evidence is missed

They do not replace:

- local repo inspection
- local workspace verification
- QA evidence requirements
- Linear status/label governance
- CJ scope judgment

## Important distinction: deeplink vs Linear integration task

Assigning an issue to Codex or mentioning `@Codex` in Linear is not the same as using a local Codex deeplink.

Those Linear integration actions create a Codex cloud task. They should be treated as explicit cloud-task delegation, not as part of routine `update Linear` hygiene.

For the current BitPod safety posture, routine issue truth-updating must preserve existing assignee/delegate fields by default and must not trigger Codex cloud work implicitly.

## Use the deeplink only if all are true

1. The issue has a clear executable task, not just an idea.
2. The repo scope is known, or narrow enough to discover quickly.
3. The description/comments contain the context that would otherwise be manually pasted into Codex.
4. Codex is actually expected to begin implementation, debugging, or review work now.

## Do not use the deeplink if any are true

1. The issue is still backlog fuzz or product-shaping work.
2. Scope still depends on CJ judgment before execution can start.
3. The important context lives mostly outside Linear.
4. The task is really for planning/orchestration rather than Codex execution.

## Minimum issue quality before deeplink

- specific title
- expected outcome stated
- relevant repo known or inferable
- blockers or dependencies mentioned when they matter
- relevant evidence, comments, or attachments already present

## BitPod workflow interpretation

1. CJ decides the issue is Codex-ready.
2. Linear deeplink opens the issue in Codex with better initial context.
3. Codex still verifies repo truth locally before acting.
4. Codex works in the local workspace, not by trusting Linear alone.
5. QA, evidence, and Linear state changes still follow existing BitPod rules.
6. Routine issue hygiene must preserve existing assignee/delegate fields by default.
7. Routine issue hygiene must not assign/delegate the issue to Codex or mention `@Codex` unless CJ explicitly wants a cloud task.

## Good immediate use cases

- scoped bug fixes
- scoped cleanup work
- review or debugging tasks
- implementation tasks with long useful comment history

## Bad immediate use cases

- vague strategy tickets
- broad architecture tickets with unresolved framing
- multi-repo ambiguity without prior scope narrowing
- tasks that still need CJ to define what "done" means

## Current conclusion

For BitPod right now:

- deeplink = useful intake shortcut
- not = autonomous delegation
- not = substitute for local workspace truthfulness checks
