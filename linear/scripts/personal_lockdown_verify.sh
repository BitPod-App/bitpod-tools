#!/usr/bin/env bash
set -euo pipefail

OUT="${1:-}"
if [[ -z "$OUT" ]]; then
  ts="$(date -u +%Y-%m-%dT%H%M%SZ)"
  OUT="/tmp/personal_lockdown_verify_${ts}.md"
fi

{
  echo "# Personal Lockdown Verify"
  echo
  echo "- Date (UTC): $(date -u +"%Y-%m-%d %H:%M:%S")"
  echo
  echo "## gh auth status"
  echo
  echo '```'
  gh auth status 2>&1 || true
  echo '```'
  echo
  echo "## Org app installations"
  echo
  echo '```'
  gh api /orgs/BitPod-App/installations --jq '.installations[] | [.id,.app_slug,.repository_selection,.account.login] | @tsv' 2>&1 || true
  echo '```'
  echo
  echo "## Org repo reachability"
  echo
  echo '```'
  gh repo list BitPod-App --limit 200 --json name,visibility,url --jq '.[] | [.name,.visibility,.url] | @tsv' 2>&1 || true
  echo '```'
  echo
  echo "## PR read smoke"
  echo
  echo '```'
  gh pr list -R BitPod-App/bitpod-tools --limit 5 --json number,title,state,url --jq '.[] | [.number,.state,.title,.url] | @tsv' 2>&1 || true
  echo '```'
} > "$OUT"

echo "$OUT"
