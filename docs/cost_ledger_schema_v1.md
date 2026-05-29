# BitPod All-Cost Ledger — Schema v1

**Owner:** Taylor01 (Cost Steward)
**Created:** 2026-05-28
**Related:** BIT-381, BIT-380

---

## Purpose

A durable, public-safe cost ledger for tracking all AI/runtime spend, subscriptions, SaaS bills, domains, and one-time purchases. Designed to let Taylor01 produce monthly budget snapshots, anomaly decisions, and cut/keep/downgrade recommendations.

## Ledger format

Each cost entry is a JSON object on a single line (JSONL). Path: `bitpod-tools/artifacts/cost-ledger/ledger_<YYYY-MM>.jsonl`

### Required fields

| Field | Type | Description |
|---|---|---|
| `id` | string | Unique slug: `<vendor>_<product_short>_<YYYY-MM>` |
| `month` | string | Billing month: `YYYY-MM` |
| `vendor` | string | Provider name, e.g. `openai`, `anthropic`, `xai`, `linear`, `github`, `cloudflare` |
| `product` | string | Specific product/plan/model, e.g. `gpt-5.4-mini`, `claude-opus-4-7`, `pro-plan` |
| `billing_type` | enum | `api_usage` \| `subscription` \| `one_time` |
| `recurrence` | enum | `monthly` \| `annual` \| `per_use` \| `one_time` |
| `amount_usd` | float \| null | Cost in USD. `null` if unknown/unverifiable without billing API |
| `amount_confidence` | enum | `exact` \| `estimated` \| `unknown` |
| `baseline_clean` | bool | `true` = known-clean baseline spend. `false` = may include bug/polluted spend (e.g. April token-leak window) |

### Optional fields

| Field | Type | Description |
|---|---|---|
| `project_agent` | string | `taylor01` \| `vera` \| `cj` \| `shared` \| `infra` |
| `model_route` | string | Full model ID if `api_usage`, e.g. `gpt-5.4-mini` |
| `session_count` | int | Hermes session count for the period (if known) |
| `message_count` | int | Message count for the period (if known) |
| `recommendation` | enum | `keep` \| `cut` \| `downgrade_model` \| `move_to_subscription` \| `stop_automation` \| `investigate` |
| `recommendation_reason` | string | Short rationale |
| `notes` | string | Free-form. No secret values, vault IDs, or private payment details |

### Pollution flag convention

- `baseline_clean: true` — confirmed clean baseline spend (no known bugs, runaway automation, or investigation overhead)
- `baseline_clean: false` — period includes known polluted spend (April 2026 token-leak investigation, runaway retries, unexpected automation spikes, or attribution uncertainty)

Set `baseline_clean: false` for any cost row where:
- The billing month overlaps the April 2026 token-leak investigation window
- The session or automation type was associated with a runaway/retry pattern
- The amount is anomalous vs prior months without a clear production reason

## Public-safety rules

- Never record: raw token values from billing invoices, exact invoice amounts from private billing dashboards, secret paths, vault IDs, field IDs, keychain labels, or bootstrap command parameters
- Estimated amounts from public pricing × session count are safe to record
- Mark any amount derived from a private billing dashboard as `amount_confidence: exact` and note the source only as the vendor name (not the dashboard URL or account ID)
- Do not store private payment method details, credit card numbers, or bank info

## Rollup query pattern

To produce a monthly summary:
```
jq -s 'group_by(.billing_type) | map({type: .[0].billing_type, total_usd: [.[].amount_usd | numbers] | add})' ledger_YYYY-MM.jsonl
```

To find polluted spend:
```
jq 'select(.baseline_clean == false)' ledger_YYYY-MM.jsonl
```

To find cut/downgrade candidates:
```
jq 'select(.recommendation == "cut" or .recommendation == "downgrade_model")' ledger_YYYY-MM.jsonl
```
