# Tower Scoring and Goodhart Defense

## Core idea
The Tower ranks Decks by **forward predictive performance**, not popularity.

## What gets scored (start small)
Prefer probabilistic targets (so we can score calibration):
- Probability BTC 30D return > 0
- Probability “risk-on” regime next week
- Probability a liquidity regime shift by date D

## Metrics (recommended)
- **Brier score** for binary probabilistic events (lower is better)
- Track accuracy too, but calibration is harder to game.

## Goodhart defenses
- Rank is determined by performance score, not zaps.
- Zaps may influence “Trending,” never “Top.”
- Edits create new versions; stable configs earn track record.
- Require disclosure (deviation/personalization index).
