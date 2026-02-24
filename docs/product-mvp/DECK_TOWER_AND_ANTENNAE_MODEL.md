# Deck + Tower + Antenna Array Model
*MVP canon for BitPod’s user-facing metaphor + lifecycle.*

## Why this exists
We want language that is:
- **intuitive** for users,
- **precise** for engineering,
- **auditable** by default,
- and consistent with **block-height time**.

This document locks the “radio” model: how Decks behave, how the Tower ranks them, and how podcasts (Antenna Arrays) fit without becoming “authority.”

## One‑sentence mental model
🎙️ **Antenna Arrays detect**, 🎛️ **Decks tune + broadcast**, 🗼 **the Tower ranks broadcasts by SNR** under real **Channel Conditions**.

## Objects

### 🗼 Tower
The **Tower** is the public ranking surface (leaderboard).  
It ranks **Deck broadcasts** by forward-scored performance.

**The Tower ranks by:** performance (SNR), not popularity.

### 🎛️ Deck
A **Deck** is the user-owned configuration/workspace:
- it holds settings (weights, toggles, enabled instruments),
- it produces outputs (broadcasts),
- it has versions/presets,
- it earns a track record over time.

> Note: A Deck may contain internal modules that behave like transceivers (receive + transmit), but **“Transceiver” is not the primary user-facing noun**.

### 🧰 Control Panel
The **Control Panel** is the UI workspace where you tune a Deck:
- faders/sliders (weights),
- toggles (modules/instruments),
- live preview (waveforms, delta vs baseline),
- current SNR readout.

### 📡 Antenna Array (Podcasts)
An **Antenna Array** is a curated set of **podcast feeds** used for early detection of emerging narratives/events (“unknown unknowns”).

**Antennae detect; they do not verify.**  
Verification requires corroboration via Fiat Authority and/or Chain Truth sources.

### 📻 Baseline (Canonical Broadcast)
The **Baseline** is the default bitregime-core configuration + output.

- Always runs
- Always auditable
- Always used as the comparison point for deltas, scoring, and (later) adoption

## Deck broadcast states (explicit + block-time)

### 📡 LIVE
- Broadcasting is ON
- Track record accrues in **blocks**
- Eligible for serious scoring and Tower ranking (if public)

### 🛠️ RECALIBRATING
- Temporarily Off-Air
- Track record does **not** accrue blocks  
- **Off-Air blocks** accumulate during this period

### 📴 OFF-AIR
- Not broadcasting
- No block accrual
- Not rank-eligible
- Used for drafts/parked Decks

*(Optional later: ⏳ PENDING for “go LIVE at next block.”)*

## Timekeeping (canonical = block height)
BitPod uses **block height** as canonical time for:
- LIVE duration,
- RECALIBRATING downtime,
- track record earned.

Examples:
- “LIVE for 12,480 blocks”
- “RECALIBRATING — Off-Air for 1,248 blocks”
- “Track record earned over 30,000 blocks”

## Performance (SNR is the score)

### ✅ SNR (Signal-to-Noise Ratio) = primary score
**SNR is the primary performance indicator for a Deck’s broadcast.**

Intuition:
- Higher SNR → more accurate, better calibrated, more stable across conditions.

### What “noise” means here
Noise is not “bad vibes.”  
Noise is instability / overfitting / unreliable confidence under forward scoring.

**Signal is always positive.**  
Noise is what reduces SNR.

## Channel Conditions (context overlay)
Channel Conditions describe the environment in which predictions are made:

- 🌤️ **Clear** — stable, low interference
- 🌥️ **Choppy** — transitioning, noisy
- 🌩️ **Signal Disruption** — high volatility / fast regime shifts / attention shocks

Shown on:
- the Tower (global conditions),
- each run/report (local conditions).

## Tower movement language (rank changes)
Use physics-flavored movement terms:

- **gain / fade** → small moves
- **spike / drop** → large moves over short block time

Avoid “dip” in default UI.

## Source epistemology (keeps the metaphor honest)
We separate “truth” from “market-moving authority”:

- ⛓️ **Chain Truth Sources** — on-chain reality (hard constraints)
- 🏛️ **Fiat Authority Sources** — official sources that move markets (even if contested)
- 🧪 **Independent Reality Checks** — cross-check datasets (e.g., Trueflation alongside CPI)

Antenna Array inputs may trigger investigation, but they never become truth without verification.

## Disclosure (always-on)
Every Deck run must disclose:
- **Deviation from Baseline**
- configuration version/hash
- evidence cutoffs + manifest

No “mystery sauce.”
