#!/usr/bin/env bash
set -euo pipefail

DOMAIN="${1:-bitpod.app}"
OUT="${2:-}"

if [[ -z "$OUT" ]]; then
  ts="$(date -u +%Y-%m-%dT%H%M%SZ)"
  OUT="/tmp/email_auth_probe_${DOMAIN//./_}_${ts}.md"
fi

{
  echo "# Email Auth Probe"
  echo
  echo "- Date (UTC): $(date -u +"%Y-%m-%d %H:%M:%S")"
  echo "- Domain: \`$DOMAIN\`"
  echo
  echo "## Public DNS"
  echo
  echo '```bash'
  echo "dig +short TXT $DOMAIN"
  echo "dig +short TXT _dmarc.$DOMAIN"
  echo "dig +short MX  $DOMAIN"
  echo '```'
  echo
  echo "TXT $DOMAIN:"
  dig +short TXT "$DOMAIN" || true
  echo
  echo "TXT _dmarc.$DOMAIN:"
  dig +short TXT "_dmarc.$DOMAIN" || true
  echo
  echo "MX $DOMAIN:"
  dig +short MX "$DOMAIN" || true
  echo
  echo "## Cloudflare API probe (optional)"
  echo
  if [[ -z "${CLOUDFLARE_API_TOKEN:-}" ]]; then
    echo "- CLOUDFLARE_API_TOKEN not set; skipped API probe."
  else
    zresp="$(curl -sS -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
      -H "Content-Type: application/json" \
      "https://api.cloudflare.com/client/v4/zones?name=$DOMAIN&status=active")"
    zid="$(echo "$zresp" | jq -r '.result[0].id // empty')"
    if [[ -z "$zid" ]]; then
      echo "- Zone lookup failed:"
      echo "$zresp" | jq -c '{success,errors,messages}' || true
    else
      echo "- Zone lookup success, zone_id=$zid"
      dresp="$(curl -sS -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
        -H "Content-Type: application/json" \
        "https://api.cloudflare.com/client/v4/zones/$zid/dns_records?per_page=5")"
      echo "- DNS records probe:"
      echo "$dresp" | jq -c '{success,errors,messages,result_count:(.result|length? // 0)}' || true
    fi
  fi
} > "$OUT"

echo "$OUT"
