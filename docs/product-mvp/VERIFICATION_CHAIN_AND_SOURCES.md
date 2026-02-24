# Verification Chain and Sources

## Goal
Convert “someone said X is happening” into verified events with evidence, provenance, and fail-closed behavior.

## Verification chain
1) Claim detected (often via Antenna Array)  
2) Event hypothesis created  
3) Source retrieval  
4) Corroboration rules applied  
5) Event verified or rejected  
6) Event lifecycle starts (decay/expiry)  
7) Weight redistribution happens deterministically  
8) Artifacts produced (logs, manifests, hashes)

## Source classes (product language)
- ⛓️ **Chain Truth Sources**: on-chain reality and transparent derivations  
- 🏛️ **Fiat Authority Sources**: official releases that move markets even if contested  
- 🧪 **Independent Reality Checks**: cross-check datasets  
- 🎙️ **Antenna Array**: detection only (never verifies)

## Required artifacts
- `verification_log.json`
- `event_state.json`
- `run_manifest.json`
