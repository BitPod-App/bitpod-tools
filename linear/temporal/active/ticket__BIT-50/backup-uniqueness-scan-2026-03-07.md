# Backup Uniqueness Scan (2026-03-07)

Related issue: https://linear.app/bitpod-app/issue/BIT-50/retire-legacy-local-backup-workspace-after-migration-hardening-bitpod

## Backup docs vs Active docs
- Backup-only file paths: 42
- Sample backup-only paths:
  - .DS_Store
  - .gitignore
  - README.md
  - archive/learnings/README.md
  - archive/learnings/decision-2026-02-27-mvp-gap-matrix-weekly-bundle.md
  - archive/learnings/decision-2026-02-27-provenance-two-axis-model.md
  - archive/learnings/incident-2026-02-27-provenance-assumption-mismatch.md
  - archive/learnings/retro-2026-02-27-cleanup-audit-drift.md
  - archive/reference-candidates/README.md
  - process/.DS_Store
  - process/anti-drift-playbook.md
  - process/canonical-path-contract.md
  - process/local-workspace-cleanup-runbook.md
  - process/project-sources/00_CANONICAL_REFS_AND_PINS_v1.json
  - process/project-sources/00_CANONICAL_REFS_AND_PINS_v1.md
  - process/project-sources/01_PRODUCT_INTENT_ONE_PAGER_v1.md
  - process/project-sources/02_JTBD_AND_CORE_FLOWS_MIN_v1.md
  - process/project-sources/03_DECISIONS_LOG_MIN_v1.md
  - process/project-sources/10_TECHNICAL_CONTRACTS_INDEX_v1.md
  - process/project-sources/11_RUNTIME_GOVERNANCE_CONTRACT_v1.md

## Backup tools vs Active tools
- Backup-only file paths: 32
- Sample backup-only paths:
  - .DS_Store
  - .gitignore
  - artifacts/cost-meter/cost_events.jsonl
  - audit_ctl.sh
  - chatgpt-prompts/README.md
  - chatgpt-prompts/weekly-btc/weekly-btc-prompts.md
  - costs/__pycache__/cost_meter.cpython-311.pyc
  - costs/cost_ctl.py
  - costs/cost_meter.py
  - docs/README.md
  - gpt_bridge/.env
  - gpt_bridge/.gitignore
  - gpt_bridge/README.md
  - gpt_bridge/ask_gpt.py
  - gpt_bridge/ask_gpt.sh
  - gpt_bridge/ask_once.sh
  - gpt_bridge/bridge_chat.py
  - gpt_bridge/bridge_chat.sh
  - gpt_bridge/bridge_ctl.sh
  - gpt_bridge/config.example.env

## Backup taylor-runtime vs Active bitpod-taylor-runtime
- Backup-only file paths: 111
- Sample backup-only paths:
  - artifacts/.DS_Store
  - artifacts/logs/taylor_run_20260222T231302Z.log
  - artifacts/logs/taylor_run_20260223T011818Z.log
  - artifacts/zulip/.DS_Store
  - artifacts/zulip/BitPod/.DS_Store
  - artifacts/zulip/BitPod/42bbe6c/20260222T233953Z/manifest.json
  - artifacts/zulip/BitPod/42bbe6c/20260222T233953Z/pr_post.json
  - artifacts/zulip/BitPod/42bbe6c/20260222T233953Z/qa_review.md
  - artifacts/zulip/BitPod/42bbe6c/20260222T233953Z/session_summary.md
  - artifacts/zulip/BitPod/42bbe6c/20260222T233953Z/worth_remembering.json
  - artifacts/zulip/BitPod/a-frog/20260223T031433Z/manifest.json
  - artifacts/zulip/BitPod/a-frog/20260223T031433Z/pr_post.json
  - artifacts/zulip/BitPod/a-frog/20260223T031433Z/qa_review.md
  - artifacts/zulip/BitPod/a-frog/20260223T031433Z/session_summary.md
  - artifacts/zulip/BitPod/a-frog/20260223T031433Z/worth_remembering.json
  - artifacts/zulip/BitPod/a-frog/20260224T022121Z/manifest.json
  - artifacts/zulip/BitPod/a-frog/20260224T022121Z/qa_review.json
  - artifacts/zulip/BitPod/a-frog/20260224T022121Z/qa_review.md
  - artifacts/zulip/BitPod/a-frog/20260224T022121Z/session_summary.md
  - artifacts/zulip/BitPod/a-frog/20260224T022121Z/worth_remembering.json

## Backup bitpod vs Active bitpod
- Backup-only file paths: 7093
- Sample backup-only paths:
  - .venv/.DS_Store
  - .venv/lib/.DS_Store
  - .venv/lib/python3.9/.DS_Store
  - .venv311/.DS_Store
  - .venv311/bin/Activate.ps1
  - .venv311/bin/activate
  - .venv311/bin/activate.csh
  - .venv311/bin/activate.fish
  - .venv311/bin/distro
  - .venv311/bin/httpx
  - .venv311/bin/normalizer
  - .venv311/bin/openai
  - .venv311/bin/pip
  - .venv311/bin/pip3
  - .venv311/bin/pip3.11
  - .venv311/bin/tqdm
  - .venv311/bin/yt-dlp
  - .venv311/lib/.DS_Store
  - .venv311/lib/python3.11/.DS_Store
  - .venv311/lib/python3.11/site-packages/.DS_Store

## Backup bitregime-core vs Active bitregime-core
- Backup-only file paths: 3
- Sample backup-only paths:
  - .DS_Store
  - PIPELINE_STAGE_CONTRACT.md
  - artifacts/intake/runs/intake_jack_mallers_show_20260228T102052Z.json

## Backup-only directories without direct active counterpart
- App Downloads: 0 files
- artifacts: 19 files
