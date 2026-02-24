# BitPod North Star

## What BitPod is
BitPod is a **Bitcoin regime intelligence system** with two layers:

1) **Baseline Engine (bitregime-core)** — deterministic, auditable, evidence-first regime outputs from verified inputs.  
2) **Decks (Personalization Layer)** — user-configurable “mixes” that adjust weights and optional feeds/skills **on top of** the baseline.

The product is only real if the baseline is real.

## Non‑negotiable order of operations
### North Star #1: Baseline credibility (first)
Before public decks/leaderboards/social:
- The baseline must achieve **high performance** under **published scoring rules** using **forward predictions** + **verifiable evidence**.
- If baseline can’t beat randomness under its own rules, we ship **nothing user-facing**.

## Core objects
### Baseline
Canonical reference run of bitregime-core:
- deterministic inputs → deterministic outputs
- strict evidence logging
- versioned artifacts + hashes
- forward-scored vs reality on defined horizons

Baseline always runs.

### Deck
A Deck is a named configuration that modifies the system in controlled ways:
- weight adjustments within a stable factor ontology
- optional enabling of approved feeds/skills
- explicit metadata: author, version, provenance

A Deck never replaces baseline; it layers on top.

### Personalization Delta
Every Deck report must disclose:
- what changed vs baseline (weights/skills/sources)
- how much it changed (delta magnitudes)
- a single “Personalization Index” (0–100) so any viewer can see customization extent

## Invariants (glued‑in constraints)
- Determinism: same inputs → same outputs + same hashes  
- Evidence-first verification: fail-closed, logged sources + cutoffs  
- Stable factor ontology: buckets don’t drift; only weights move inside them  
- Antennae are detectors, not authorities  
- Baseline always computable and always publishable  
- Explainability: outputs trace to inputs, events, and weights  
- Stable configs exist for scoring; no moving-goalposts rankings  

## The product promise
BitPod lets users:
- run baseline regime engine
- apply a deck (personalization)
- see delta vs baseline (honest disclosure)
- evaluate decks by forward performance (Tower ranking)
- share outputs publicly with credible customization disclosure

But we earn this only by nailing baseline first.
