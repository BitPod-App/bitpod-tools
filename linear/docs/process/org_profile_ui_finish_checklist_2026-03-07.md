# Org Profile UI Finish Checklist (BIT-55)

Related issue: https://linear.app/bitpod-app/issue/BIT-55/org-profile-cleanup-pass-readmelogo-placeholderpinsdescriptions

## Completed via API/CLI

- Org display name: `BitPod App`
- Org bio: `Publishing Bitcoin theses with disciplined signal and execution.`
- Repo descriptions standardized for all six org repos.

## Remaining UI-only tasks

1. Upload placeholder org avatar/logo.
2. Pin 2–3 repos on org profile.

Recommended pins (per agreed structure):
- Main product repo: `sector-feeds`
- Docs/spec/process repo: `bitpod-docs`
- Infra/tooling repo: `bitpod-tools`

## Why UI-only

Attempted GitHub GraphQL mutation from CLI:
- `pinRepository` mutation is not exposed in this API schema for this context.
- Result: pinning must be completed in GitHub org profile UI.

## Verification after UI changes

- Visit org page and confirm exactly 3 pinned repos are visible.
- Confirm avatar renders correctly in light and dark theme.
