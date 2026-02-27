# Weekly BTC Prompt Pack (Ad Hoc + Recurring)

Use these prompts in order.

## 0) Run Preflight Rule (always send first)

```text
Operating rule for this run:
- Mallers links are optional freshness inputs, not hard dependencies.
- If Mallers fetch fails, continue with independent web research and clearly note missing Mallers intake.
- Do not assume Codex artifacts exist unless explicitly provided in this chat.
- GPT is narrative-only: do not treat narrative reasoning as a substitute for missing critical datasets.
Confirm these 3 rules, then run the Weekly BTC Data Update + Output Report.
```

## 1) Run Prompt (standard)

```text
Run the Weekly BTC Data Update + Output Report now using your own web research and reasoning.

Ignore Codex pipeline assumptions for this run. Do not block on Codex artifacts.

Use the latest Mallers transcript in this chat only as a freshness steering input (what to investigate), not as an authoritative source for market facts.

Requirements:
1) Verify key claims with current sources; include exact dates and links.
2) Keep the normal report structure:
   - driver scoreboard
   - 7-day / 30-day probability map
   - falsifiers
   - data gaps
3) Clearly separate:
   - Mallers-triggered search directives
   - verified market/macro data used for scoring
4) If a dataset is missing, continue with best available substitutes and explicitly label confidence impacts.

Generate the full report now.
```

## 2) Reasoning Trace Prompt (always run after report)

```text
Append a Reasoning Trace for this exact report.

Return BOTH:
1) Markdown section called "Reasoning Trace"
2) JSON block called "reasoning_trace_json"

Include:
- claims_considered: [{claim, used_in_final (true/false), reason}]
- sources_checked: [{url, publisher, published_date, accessed_date}]
- rejected_claims: [{claim, rejection_reason}]
- assumptions: [{assumption, impact}]
- module_confidence: [{module, confidence_0_to_100, rationale}]
- weight_changes: [{driver, previous_weight, new_weight, why}]
- falsifiers_linked: [{falsifier, driver, threshold_or_condition}]

Rules:
- Use exact dates (e.g., "February 26, 2026"), not relative dates.
- Keep it auditable and concise.
- Do not restate the full report; provide traceability only.
```

## 3) Fast/Budget Mode (if runs too long)

```text
Re-run in bounded mode:
- Maximum 12 sources total
- Prioritize primary/official sources first
- If unresolved after 8 minutes, return partial report with "blocked_items" and best-effort scoreboard.

Still include:
- 7d/30d probabilities
- falsifiers
- confidence impacts
- concise reasoning trace JSON
```

## 4) Optional Mallers-First Reminder

```text
Before finalizing, explicitly list "Mallers-triggered checks executed" and whether each changed any driver score.
```

## 5) Strict Repair Run (Data Backfill Only)

```text
STRICT REPAIR RUN — DATA BACKFILL ONLY (no narrative)

Target run date: 2026-02-26 UTC.
Fill only these missing critical datasets:

1) spot_btc (authoritative spot print, USD)
2) etf_net_flows (issuer-level, latest session)
3) derivatives_funding_oi_liquidations (BTC funding, BTC OI, BTC liquidations)
4) move_index (rates volatility)

Return a single markdown table:
metric | value | timestamp_utc | source_url | source_type(primary/secondary) | confidence_0_to_100 | notes

Rules:
- Prefer primary sources; if unavailable, use best secondary and label it.
- If not verifiable, keep as missing with exact reason.
- No scoreboard, no probabilities, no commentary.
```

## 6) Strict Regeneration After Backfill

```text
Using the previous STRICT INCOMPLETE report plus the backfill table you just produced, regenerate STRICT report.

Rules:
- If 2+ critical datasets still missing: keep status INCOMPLETE.
- If fewer than 2 missing: produce COMPLETE report with scoring_table + probability_map + falsifiers.
- Include updated data_table and reasoning_trace_json.
```

## 7) Strict Single-Pass (Context-Safe)

```text
Run a STRICT single-pass Weekly BTC report without relying on prior chat state.

Fetch and verify all critical datasets in this run:
1) spot_btc
2) etf_net_flows (issuer-level latest session)
3) derivatives_funding_oi_liquidations
4) move_index
5) dfii10
6) dgs10
7) broad_usd (or dxy proxy)
8) usdjpy
9) rrp
10) tga

Rules:
- If 2+ critical datasets are missing or confidence-blocked (<60), return INCOMPLETE and do NOT output scoring/probability.
- If fewer than 2 are missing/blocked, return COMPLETE with scoring_table + 7d/30d probability_map + falsifiers.
- Do not assume Codex artifacts unless explicitly provided in this chat.
- Mallers is optional freshness steering only.
- GPT cannot satisfy missing critical datasets by explanation, inference, or narrative fallback.

Required output:
A) status_header (STRICT + COMPLETE/INCOMPLETE)
B) data_table: metric | value | timestamp_utc | source_url | source_type | confidence_0_to_100 | confidence_override_reason | scoring_usable_yes_no
C) blocked_items (if any)
D) scoring_table + probability_map (only if COMPLETE)
E) falsifiers (only if COMPLETE)
F) reasoning_trace_json
```
