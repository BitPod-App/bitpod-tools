# Linear Type Classifier Corrections v1

Status: Active learning log
Owner: Product Development
Machine source: `linear/contracts/linear_type_classifier_v1.json`

## Purpose

Record CJ corrections to automation hygiene issue-type or routing decisions in one durable place.

This file is the human-readable learning surface. It is not enough by itself: every correction that changes future behavior must also be converted into the machine-readable classifier or a classifier test fixture.

## Correction workflow

When automation hygiene mutates Linear issue type/routing and CJ corrects it:

1. Add one short entry below.
2. Summarize the corrected rule in plain language.
3. Update `linear/contracts/linear_type_classifier_v1.json` or add a classifier test fixture in the same run/PR.
4. Reference the changed rule/test in the audit report back to CJ.

Helper:
- `python3 linear/scripts/record_type_classifier_correction.py` can append an entry here and (optionally) add a machine-enforced fixture row in `linear/tests/fixtures/linear_type_classifier_corrections_v1.json` (BIT-441).

## Entry format

```md
### YYYY-MM-DD — short correction title

- Source: BIT-000 or hygiene audit run link
- Automation chose: Type / route
- CJ correction: Type / route
- Rule learned: one sentence
- Machine update: classifier rule/test path or `pending`
```

## Corrections

_No corrections recorded yet._
