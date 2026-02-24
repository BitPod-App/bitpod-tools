# Roadmap Gates (Capability-Based, Not Date-Based)

## Baseline-first gates
### E0 — Baseline produces first deterministic run
Proof artifacts:
- score_report.json + score_report.md
- run_manifest.json (hashes)
- verification_log.json

### E1 — Forward scoring pipeline exists
Proof:
- prediction packets frozen with cutoffs + hashes
- scoring job evaluates predictions when reality arrives

### E2 — Baseline credibility threshold achieved
Proof:
- baseline beats naive benchmarks on chosen metrics
- stable results over sufficient sample window
