#!/usr/bin/env bash
set -euo pipefail

ROOT="/Users/cjarguello/bitpod-app"
# Guardrail: this runner is read-only. It never renames/moves/deletes files.
# Rename cleanup is a separate manual workflow (quarantine first, then decide).
NOW="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

print_header() {
  echo "Audit Control | $1"
  echo "Timestamp: $NOW"
}

normalize() {
  tr '[:upper:]' '[:lower:]'
}

has_phrase() {
  local haystack="$1"
  local needle="$2"
  [[ "$haystack" == *"$needle"* ]]
}

repo_sync_status() {
  local repo_path="$1"
  local require_fresh="$2"
  local name
  name="$(basename "$repo_path")"
  local branch upstream dirty ahead behind head_sha upstream_sha head_eq_upstream remote_fresh
  branch="$(cd "$repo_path" && git rev-parse --abbrev-ref HEAD)"
  upstream="$(cd "$repo_path" && git rev-parse --abbrev-ref --symbolic-full-name @{u} 2>/dev/null || true)"
  dirty="$(cd "$repo_path" && git status --porcelain | wc -l | tr -d ' ')"
  ahead=0
  behind=0
  head_sha="$(cd "$repo_path" && git rev-parse HEAD)"
  upstream_sha=""
  head_eq_upstream="unknown"
  remote_fresh="false"

  if [[ "$require_fresh" -eq 1 ]]; then
    (cd "$repo_path" && git fetch --all --prune >/dev/null 2>&1 || true)
    remote_fresh="true"
  fi

  if [[ -n "$upstream" ]]; then
    local ab
    ab="$(cd "$repo_path" && git rev-list --left-right --count HEAD...@{u})"
    ahead="$(printf '%s' "$ab" | awk '{print $1}')"
    behind="$(printf '%s' "$ab" | awk '{print $2}')"
    upstream_sha="$(cd "$repo_path" && git rev-parse @{u})"
    if [[ "$head_sha" == "$upstream_sha" ]]; then
      head_eq_upstream="true"
    else
      head_eq_upstream="false"
    fi
  fi

  local label reason
  if [[ -z "$upstream" ]]; then
    label="UNVERIFIABLE"
    reason="cannot verify remote parity"
  elif [[ "$dirty" -gt 0 ]]; then
    label="NOT 1:1"
    reason="local changes only"
  elif [[ "$require_fresh" -eq 1 && "$ahead" -eq 0 && "$behind" -eq 0 && "$head_eq_upstream" == "true" ]]; then
    label="1:1 PORCELAIN COMPLETE FRESH MATCH"
    reason="no diff found"
  elif [[ "$require_fresh" -eq 1 ]]; then
    label="NOT 1:1"
    reason="remote drift"
  else
    label="NOT VERIFIED FOR 1:1"
    reason="remote not refreshed in this run"
  fi

  local clean_state="false"
  [[ "$dirty" -eq 0 ]] && clean_state="true"
  echo "- $name: $label ($reason; fetch_fresh=$remote_fresh, branch=$branch, upstream=${upstream:-none}, clean=$clean_state, dirty_items=$dirty, ahead=$ahead, behind=$behind, head_eq_upstream=$head_eq_upstream)"
}

run_quick() {
  local require_fresh="${1:-0}"
  print_header "T1 Quick"
  echo "[top-level]"
  find "$ROOT" -maxdepth 1 -mindepth 1 -type d -exec basename "{}" ";" | sort | sed 's/^/- /'
  echo "[top-level files]"
  find "$ROOT" -maxdepth 1 -mindepth 1 -type f -exec basename "{}" ";" | sort | sed 's/^/- /'

  echo "[repo health]"
  local repos=("bitpod" "bitregime-core" "docs" "taylor-runtime" "tools")
  local total_dirty=0
  for r in "${repos[@]}"; do
    local dirty
    dirty="$(cd "$ROOT/$r" && git status --short | wc -l | tr -d ' ')"
    local branch
    branch="$(cd "$ROOT/$r" && git rev-parse --abbrev-ref HEAD)"
    total_dirty=$((total_dirty + dirty))
    echo "- $r: dirty_items=$dirty branch=$branch"
  done

  echo "[repo 1:1 status]"
  for r in "${repos[@]}"; do
    repo_sync_status "$ROOT/$r" "$require_fresh"
  done

  echo "[local-workspace queue health]"
  local incoming=0
  local trash=0
  local refs=0
  local refs_active=0
  local refs_archive=0
  local refs_trash=0
  local pm=0
  [[ -d "$ROOT/local-workspace/incoming-clutter" ]] && incoming="$(find "$ROOT/local-workspace/incoming-clutter" -type f | wc -l | tr -d ' ')"
  [[ -d "$ROOT/local-workspace/trash-delete" ]] && trash="$(find "$ROOT/local-workspace/trash-delete" -type f | wc -l | tr -d ' ')"
  if [[ -d "$ROOT/local-workspace/working-files/reference-candidates" ]]; then
    refs="$(find "$ROOT/local-workspace/working-files/reference-candidates" -type f | wc -l | tr -d ' ')"
    [[ -d "$ROOT/local-workspace/working-files/reference-candidates/active" ]] && refs_active="$(find "$ROOT/local-workspace/working-files/reference-candidates/active" -type f | wc -l | tr -d ' ')"
    [[ -d "$ROOT/local-workspace/working-files/reference-candidates/archive" ]] && refs_archive="$(find "$ROOT/local-workspace/working-files/reference-candidates/archive" -type f | wc -l | tr -d ' ')"
    [[ -d "$ROOT/local-workspace/working-files/reference-candidates/trash" ]] && refs_trash="$(find "$ROOT/local-workspace/working-files/reference-candidates/trash" -type f | wc -l | tr -d ' ')"
  fi
  [[ -d "$ROOT/local-workspace/local-cj-pm-only" ]] && pm="$(find "$ROOT/local-workspace/local-cj-pm-only" -type f | wc -l | tr -d ' ')"
  echo "- incoming_files=$incoming"
  echo "- trash_files=$trash"
  echo "- working_ref_files=$refs"
  echo "  - working_ref_active_files=$refs_active"
  echo "  - working_ref_archive_files=$refs_archive"
  echo "  - working_ref_trash_files=$refs_trash"
  echo "- pm_only_files=$pm"

  echo "[soft purge signals]"
  local trash_pending=0
  local trash_pending_days=14
  [[ -d "$ROOT/local-workspace/trash-delete" ]] && trash_pending="$(find "$ROOT/local-workspace/trash-delete" -type f -mtime +$trash_pending_days | wc -l | tr -d ' ')"
  echo "- trash_soft_purge_pending_files=$trash_pending"
  echo "- trash_soft_purge_threshold_days=$trash_pending_days"
  echo "- trash_soft_purge_mode=SOFT_ONLY (informational, no deletion)"

  local incoming_stale=0
  local incoming_stale_days=3
  [[ -d "$ROOT/local-workspace/incoming-clutter" ]] && incoming_stale="$(find "$ROOT/local-workspace/incoming-clutter" -type f -mtime +$incoming_stale_days | wc -l | tr -d ' ')"
  echo "- incoming_stale_pending_files=$incoming_stale"
  echo "- incoming_stale_threshold_days=$incoming_stale_days"

  echo "[likely duplicates estimate]"
  local tmp_canon="/tmp/audit_ctl_canon_names.txt"
  local tmp_local="/tmp/audit_ctl_local_names.txt"
  find "$ROOT/docs" "$ROOT/bitpod" "$ROOT/bitregime-core" "$ROOT/taylor-runtime" "$ROOT/tools" -type f 2>/dev/null \
    | xargs -I{} basename "{}" | sort -u > "$tmp_canon"
  local ref_candidates_root="$ROOT/local-workspace/working-files/reference-candidates"
  if [[ -d "$ref_candidates_root" ]]; then
    find "$ref_candidates_root" -type f 2>/dev/null | xargs -I{} basename "{}" | sort -u > "$tmp_local"
  else
    : > "$tmp_local"
  fi
  local likely_dups
  likely_dups="$(comm -12 "$tmp_canon" "$tmp_local" | wc -l | tr -d ' ')"
  echo "- likely_duplicate_filename_count=$likely_dups"

  echo "[reference bucket hygiene]"
  local legacy_bucket_hits
  legacy_bucket_hits="$(find "$ROOT/local-workspace/working-files/reference-candidates" -type d \( -name 'source-*' -o -name 'taylor-2.0' -o -name 'Taylor 2.0' \) 2>/dev/null | wc -l | tr -d ' ')"
  echo "- legacy_bucket_dir_hits=$legacy_bucket_hits"

  # Stop gate heuristic for quick mode.
  if [[ "$incoming" -eq 0 && "$likely_dups" -le 25 && "$legacy_bucket_hits" -eq 0 ]]; then
    echo "quick_gate=STOP_OK"
    return 0
  fi
  echo "quick_gate=ESCALATE_RECOMMENDED"
  return 10
}

run_medium() {
  print_header "T2 Medium"
  local active="$ROOT/local-workspace/working-files/reference-candidates/active"
  local archive="$ROOT/local-workspace/working-files/reference-candidates/archive"
  if [[ ! -d "$active" && ! -d "$archive" ]]; then
    echo "medium_note=no reference-candidates folder"
    echo "medium_gate=STOP_OK"
    return 0
  fi

  local tmp_in="/tmp/audit_ctl_in_sha.txt"
  local tmp_canon="/tmp/audit_ctl_canon_sha.txt"
  find "$active" "$archive" -type f -name '*.md' -print0 2>/dev/null | xargs -0 shasum -a 256 | sort > "$tmp_in" || true
  find "$ROOT/docs" "$ROOT/bitpod" "$ROOT/bitregime-core" "$ROOT/taylor-runtime" "$ROOT/tools" -type f -name '*.md' -print0 2>/dev/null \
    | xargs -0 shasum -a 256 | sort > "$tmp_canon" || true

  local scanned=0
  local exact=0
  [[ -f "$tmp_in" ]] && scanned="$(wc -l < "$tmp_in" | tr -d ' ')"
  if [[ "$scanned" -gt 0 ]]; then
    exact="$(join -j 1 "$tmp_in" "$tmp_canon" | wc -l | tr -d ' ')"
  fi

  echo "- scanned_reference_md=$scanned"
  echo "- exact_duplicate_md=$exact"

  if [[ "$exact" -le 10 ]]; then
    echo "medium_gate=STOP_OK"
    return 0
  fi
  echo "medium_gate=ESCALATE_RECOMMENDED"
  return 20
}

run_full() {
  print_header "T3 Full"
  echo "[full inventory summary]"
  find "$ROOT" -maxdepth 2 -type d | wc -l | awk '{print "- dir_count_depth2=" $1}'
  find "$ROOT" -maxdepth 2 -type f | wc -l | awk '{print "- file_count_depth2=" $1}'
  echo "[local-workspace detailed]"
  find "$ROOT/local-workspace" -maxdepth 3 -type d | sort | sed 's#^#- #'
  echo "full_complete=TRUE"
}

confirm_or_exit() {
  local message="$1"
  local noask="$2"
  if [[ "$noask" -eq 1 ]]; then
    echo "confirm_skipped=TRUE ($message)"
    return 0
  fi
  if [[ -t 0 ]]; then
    read -r -p "$message [y/N]: " ans
    [[ "${ans,,}" == "y" || "${ans,,}" == "yes" ]] || exit 0
  else
    echo "confirmation_required=$message"
    exit 3
  fi
}

main() {
  local raw="${*:-run audit}"
  local q
  q="$(printf '%s' "$raw" | normalize)"

  local noask=0
  local force_full=0
  local auto=0

  has_phrase "$q" "don't ask me for permission" && noask=1
  has_phrase "$q" "dont ask me for permission" && noask=1
  has_phrase "$q" "no ask" && noask=1
  has_phrase "$q" "force full" && force_full=1
  has_phrase "$q" "auto" && auto=1

  local tier="T1"
  if has_phrase "$q" "t3" || has_phrase "$q" "tier 3" || has_phrase "$q" "v3" || has_phrase "$q" "full"; then
    tier="T3"
  elif has_phrase "$q" "t2" || has_phrase "$q" "tier 2" || has_phrase "$q" "v2" || has_phrase "$q" "medium"; then
    tier="T2"
  elif has_phrase "$q" "t1" || has_phrase "$q" "tier 1" || has_phrase "$q" "v1" || has_phrase "$q" "quick"; then
    tier="T1"
  fi

  echo "request=\"$raw\""
  echo "resolved_tier=$tier auto=$auto force_full=$force_full noask=$noask"

  if [[ "$tier" == "T1" ]]; then
    run_quick 0 || true
    exit 0
  fi

  # T2 or T3 always start with quick.
  local quick_fresh=0
  [[ "$tier" == "T3" ]] && quick_fresh=1
  if run_quick "$quick_fresh"; then
    if [[ "$tier" == "T2" ]]; then
      echo "t2_note=quick_stop_gate_met; medium_skipped"
      exit 0
    fi
    if [[ "$tier" == "T3" && "$force_full" -eq 0 ]]; then
      if [[ "$auto" -eq 1 ]]; then
        echo "t3_note=auto_stop_after_quick"
        exit 0
      fi
      confirm_or_exit "Quick audit indicates deeper tiers may not be worth it. Continue anyway?" "$noask"
    fi
  fi

  if run_medium; then
    if [[ "$tier" == "T2" ]]; then
      exit 0
    fi
    if [[ "$tier" == "T3" && "$force_full" -eq 0 ]]; then
      if [[ "$auto" -eq 1 ]]; then
        echo "t3_note=auto_stop_after_medium"
        exit 0
      fi
      confirm_or_exit "Medium audit indicates full audit may not be worth it. Continue to full?" "$noask"
    fi
  fi

  if [[ "$tier" == "T3" ]]; then
    run_full
  fi
}

main "$@"
