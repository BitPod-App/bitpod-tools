# CI/PR Smoke Suite Post-Transfer (BIT-15)

Date: 2026-03-07
Org: `BitPod-App`

## Smoke scope

1. Local linear bot test suite (`bitpod-tools`)
2. Open PR check status across org repos

## Results

### Local tests

- Command:
  - `python3 -m unittest linear/tests/test_engine.py linear/tests/test_runtime.py linear/tests/test_e2e_flow.py`
- Result: **PASS** (`Ran 15 tests ... OK`)

### Open PR checks snapshot

| Repo/PR | Check | Result | Link |
|---|---|---|---|
| `sector-feeds` PR #29 | `audit-and-tests` | PASS | https://github.com/BitPod-App/sector-feeds/actions/runs/22724745495/job/65896502565 |
| `bitpod-tools` PR #6 | `smoke` | PASS | https://github.com/BitPod-App/bitpod-tools/actions/runs/22794130124/job/66125963344 |
| `sector-feeds` PR #28 | `audit-and-tests` | PASS | https://github.com/BitPod-App/sector-feeds/actions/runs/22677967698/job/65739925138 |
| `sector-feeds` PR #27 | `audit-and-tests` | PASS | https://github.com/BitPod-App/sector-feeds/actions/runs/22656704893/job/65667935172 |
| `bitpod-docs` PR #2 | none reported | **GAP** | https://github.com/BitPod-App/bitpod-docs/pull/2 |
| `sector-feeds` PR #26 | `audit-and-tests` | PASS | https://github.com/BitPod-App/sector-feeds/actions/runs/22595111987/job/65462946250 |

## Pass/fail summary

- PASS: all discovered active checks executed successfully.
- GAP: `bitpod-docs` PR #2 has no checks configured for branch/PR.

## Fix-forward list

1. Add minimal PR smoke workflow to `bitpod-docs` (markdown lint/link check or docs smoke).
2. Require the docs smoke check on `main` branch protection once available.
3. Re-run `gh pr checks` for `bitpod-docs` PR #2 to confirm check presence and pass state.

## Commands used

```bash
cd /Users/cjarguello/bitpod-app/bitpod-tools
python3 -m unittest linear/tests/test_engine.py linear/tests/test_runtime.py linear/tests/test_e2e_flow.py

gh search prs --owner BitPod-App --state open --limit 100 --json number,title,repository,url
# for each open PR:
# gh pr checks <num> --repo BitPod-App/<repo>
```
