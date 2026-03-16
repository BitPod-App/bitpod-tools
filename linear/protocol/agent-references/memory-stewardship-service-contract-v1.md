# Memory Stewardship Service Contract v1

## Purpose

Define a narrow, reviewable memory-write process so Taylor can preserve durable knowledge without turning chat into the database.

## Core rule

The memory steward does not write durable memory directly.

It produces a proposal artifact.
Taylor reviews that proposal.
Only approved proposals are written into durable project memory.

## Scope

In scope:

- durable memory write proposals
- contradiction scans across existing process docs
- approval logging
- proposal validation

Out of scope:

- automatic silent memory writes
- user-profile memory mutation
- hidden summarization with no artifact

## Required artifacts

### 1. Memory write proposal

A structured JSON artifact that contains:

- proposal id
- timestamp
- source artifacts
- proposed target path
- memory layer
- summary
- rationale
- confidence
- contradiction check result
- approval state

### 2. Approval log

A lightweight append-only log showing:

- proposal id
- approver
- decision
- timestamp
- target path

### 3. Contradiction scan report

A markdown artifact summarizing:

- documents scanned
- conflicting claims found
- severity
- recommended resolution path

## Memory layers

- `working`: short-lived execution context, not authoritative
- `project`: durable project operating knowledge
- `strategic`: durable CJ / BitPod operating principles
- `artifact`: references to formal runbooks, ADRs, evidence packs

## Decision policy

### Allowed without escalation

- proposal creation
- contradiction scan generation
- validation of proposal shape

### Requires Taylor approval

- any write to durable memory artifacts
- any overwrite of an existing durable memory statement
- any resolution of contradictory project guidance

### Requires CJ approval

- changes to strategic memory that alter operating philosophy
- deletion of existing durable memory artifacts

## Minimum proposal quality bar

Every proposal must include:

- exact source artifact paths
- concise summary of the proposed memory
- explicit rationale for why it should persist
- contradiction result
- confidence score

If any of the above is missing, the proposal is invalid.

## Fail-closed behavior

If contradiction status is `conflict` or approval is missing:

- do not write
- do not claim memory was updated
- emit a review-needed result only

## Initial implementation artifacts

- schema: `linear/contracts/memory_write_proposal_schema_v1.json`
- example proposal: `linear/examples/memory_write_proposal_example_v1.json`
- example approval log: `linear/examples/memory_approval_log_v1.csv`
- example contradiction scan: `linear/examples/memory_contradiction_scan_sample_2026-03-10.md`
- validator: `linear/scripts/validate_memory_proposal.py`
