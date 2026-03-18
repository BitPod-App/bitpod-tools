# Temporal Cleanup Model Correction - 2026-03-18

This note corrects earlier thread claims that the Linear temporal cleanup metadata model had already been implemented.

## What was claimed earlier

The thread described the following as if they already existed:

- a real `bitpod-tools/linear/temporal/` stage structure
- per-bucket `.temporal_meta.json` metadata
- `is_temporal=true`
- `cleanup_status=hold|purge|deleted|failed`
- a `linear_temporal_lifecycle_audit.py` script
- scheduled cleanup integration for temporal lifecycle reporting/export

## What the filesystem/code check found

A direct repo inspection on 2026-03-18 found that those claims were not true in committed repo state:

- `bitpod-tools/linear/temporal/` did not contain stage folders or bucket metadata
- no lifecycle script existed under `bitpod-tools/scripts/`
- scheduled cleanup only ran `audit_ctl.sh "run T3 audit"`
- no tests covered temporal metadata or purge export

## Correction

The model was discussed in design terms, but it was not actually committed into the surviving repo state.

## Follow-on implementation in this branch

This branch adds the missing implementation surfaces:

- `bitpod-tools/scripts/linear_temporal_lifecycle_audit.py`
- real `linear/temporal/active|closed|purge/` stage folders
- real `.temporal_meta.json` bucket metadata
- scheduled cleanup report wiring with an explicit execute gate
