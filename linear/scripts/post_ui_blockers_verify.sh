#!/usr/bin/env bash
set -euo pipefail

OUT="${1:-}"
if [[ -z "$OUT" ]]; then
  ts="$(date -u +%Y-%m-%dT%H%M%SZ)"
  OUT="/tmp/post_ui_blockers_verify_${ts}.md"
fi

{
  echo "# Post-UI Blockers Verification"
  echo
  echo "- Date (UTC): $(date -u +"%Y-%m-%d %H:%M:%S")"
  echo
  echo "## Cloudflare token scope probe (BIT-54)"
  echo
  if [[ -z "${CLOUDFLARE_API_TOKEN:-}" ]]; then
    echo "- CLOUDFLARE_API_TOKEN not set in current shell."
  else
    zone_resp="$(curl -sS -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
      -H "Content-Type: application/json" \
      "https://api.cloudflare.com/client/v4/zones?name=bitpod.app&status=active")"
    zone_id="$(echo "$zone_resp" | jq -r '.result[0].id // empty')"
    echo "- zone lookup:"
    echo "$zone_resp" | jq -c '{success,errors,messages}' || true
    if [[ -n "$zone_id" ]]; then
      dns_resp="$(curl -sS -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
        -H "Content-Type: application/json" \
        "https://api.cloudflare.com/client/v4/zones/$zone_id/dns_records?per_page=5")"
      echo "- dns_records probe:"
      echo "$dns_resp" | jq -c '{success,errors,messages,result_count:(.result|length? // 0)}' || true
    else
      echo "- zone_id unavailable; dns_records probe skipped."
    fi
  fi
  echo
  echo "## GitHub pinned repos check (BIT-55)"
  echo
  gh api graphql -f query='query { organization(login:"BitPod-App") { pinnedItems(first:10, types:REPOSITORY) { nodes { ... on Repository { name url } } } } }' \
    | jq -r '.data.organization.pinnedItems.nodes[]? | "- \(.name) :: \(.url)"'
  echo
  echo "## Target pins expected"
  echo "- sector-feeds"
  echo "- bitpod-tools"
} > "$OUT"

echo "$OUT"
