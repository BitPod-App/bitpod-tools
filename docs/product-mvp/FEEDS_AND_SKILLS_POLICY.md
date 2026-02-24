# Feeds and Instruments Policy

## Why these exist
Feeds/instruments are modular inputs that can:
- detect candidate events (Antenna Arrays)
- enrich factor computation (market/chain/flow instruments)
- provide cross-check context

They must not compromise baseline invariants.

## Safety constraints
A feed/instrument cannot:
- bypass verification
- inject unlogged weight changes
- change baseline factor ontology
- introduce hidden randomness
