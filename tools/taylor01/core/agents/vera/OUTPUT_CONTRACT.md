# Vera Output Contract

## Exact artifact names
- `verification_report.md`
- `manifest.json`

## Exact verdict tokens
- `PASSED`
- `FAILED`
- `NO_VERDICT`

## verification_report.md required sections
- Verdict
- Scope
- Evidence
- Checks Run
- Findings
- Open Questions
- Recommendation

## manifest.json minimum schema
```json
{
  "schemaVersion": "1.0",
  "agent": { "name": "Vera", "role": "QA Agent" },
  "review": {
    "targetType": "pr",
    "targetRef": "",
    "repository": "",
    "branch": "",
    "verdict": "PASSED",
    "timestamp": ""
  },
  "evidence": [],
  "checks": [],
  "artifacts": { "verificationReport": "verification_report.md" },
  "notes": [],
  "openQuestions": []
}
```

## Contract notes
- Adapter-specific receipts or comments may exist, but they do not replace these canonical artifacts.
- `NO_VERDICT` remains a first-class Vera verdict in canonical artifacts.
- Any adapter-specific external publishing label must be treated as a projection, not as the portable source of truth.
