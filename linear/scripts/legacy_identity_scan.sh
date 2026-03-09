#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "usage: $0 /ABS/PATH/report.md"
  exit 2
fi

OUT="$1"
ROOT="/Users/cjarguello/bitpod-app"
REPOS=(bitpod bitpod-tools bitpod-docs bitpod-taylor-runtime bitregime-core)
PATTERNS=("bitipod\\.com" "@bitipod\\.com" "\\bbitipod\\b")

mkdir -p "$(dirname "$OUT")"
TS="$(date -u +"%Y-%m-%d %H:%M:%SZ")"

{
  echo "# Legacy Identity Scan Report"
  echo
  echo "- UTC: ${TS}"
  echo "- Scope root: \`${ROOT}\`"
  echo "- Repos: ${REPOS[*]}"
  echo
  echo "## Counts"
  echo
  echo "| Pattern | Match count |"
  echo "|---|---:|"

  for pat in "${PATTERNS[@]}"; do
    count=0
    for repo in "${REPOS[@]}"; do
      c=$( (rg -n --hidden --glob '!.git' --glob '!node_modules' --glob '!**/.venv/**' --glob '!**/venv/**' --glob '!**/build/**' --glob '!**/dist/**' --glob '!**/linear/docs/process/legacy_identity_sweep_*' --glob '!**/linear/scripts/legacy_identity_scan.sh' "$pat" "${ROOT}/${repo}" 2>/dev/null || true) | wc -l | tr -d ' ')
      count=$((count + c))
    done
    echo "| \`${pat}\` | ${count} |"
  done

  echo
  echo "## Hits (first 20 per pattern)"
  echo
  for pat in "${PATTERNS[@]}"; do
    echo "### ${pat}"
    hits=0
    for repo in "${REPOS[@]}"; do
      while IFS= read -r line; do
        echo "- ${line}"
        hits=$((hits + 1))
        if [[ $hits -ge 20 ]]; then
          break 2
        fi
      done < <(rg -n --hidden --glob '!.git' --glob '!node_modules' --glob '!**/.venv/**' --glob '!**/venv/**' --glob '!**/build/**' --glob '!**/dist/**' --glob '!**/linear/docs/process/legacy_identity_sweep_*' --glob '!**/linear/scripts/legacy_identity_scan.sh' "$pat" "${ROOT}/${repo}" 2>/dev/null || true)
    done
    if [[ $hits -eq 0 ]]; then
      echo "- <none>"
    fi
    echo
  done

  echo "## Classification Guidance"
  echo
  echo "- Runtime/config references should be remediated."
  echo "- Historical evidence docs may retain legacy references when clearly annotated."
} > "$OUT"

echo "WROTE_REPORT ${OUT}"
