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

repo_sync_eval() {
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

  local code term meaning certainty
  if [[ -z "$upstream" ]]; then
    code=5
    term="UNLINKED"
    meaning="No upstream is configured"
    certainty="PROVEN"
  elif [[ "$dirty" -gt 0 ]]; then
    code=3
    term="LOCAL DIVERGED"
    meaning="Local changes exist"
    certainty="PROVEN"
  elif [[ "$require_fresh" -eq 1 && "$ahead" -eq 0 && "$behind" -eq 0 && "$head_eq_upstream" == "true" ]]; then
    code=1
    term="PORCELAIN"
    meaning="Perfect fresh match"
    certainty="PROVEN"
  elif [[ "$require_fresh" -eq 1 ]]; then
    code=4
    term="REMOTE DIVERGED"
    meaning="Upstream mismatch"
    certainty="PROVEN"
  else
    code=2
    term="NOT VERIFIED"
    meaning="Remote not refreshed in this run"
    certainty="UNVERIFIED"
  fi

  local clean_state="false"
  [[ "$dirty" -eq 0 ]] && clean_state="true"
  echo "$name|$code|$term|$meaning|$certainty|$branch|${upstream:-none}|$remote_fresh|$clean_state|$dirty|$ahead|$behind|$head_eq_upstream"
}

emit_parity_row() {
  local eval_row="$1"
  local reason_context="$2"
  IFS='|' read -r name code term meaning certainty branch upstream remote_fresh clean_state dirty ahead behind head_eq_upstream <<< "$eval_row"
  echo "- 1:$code | $name@$branch vs $upstream | $term - $meaning | certainty=$certainty | why=$reason_context | proof(fetch_fresh=$remote_fresh, clean=$clean_state, dirty_items=$dirty, ahead=$ahead, behind=$behind, head_eq_upstream=$head_eq_upstream)"
}

emit_parity_pulse_summary() {
  local eval_rows="$1"
  local reason_context="$2"
  local c1 c2 c3 c4 c5
  c1="$(printf '%s\n' "$eval_rows" | awk -F'|' '$2==1{n++} END{print n+0}')"
  c2="$(printf '%s\n' "$eval_rows" | awk -F'|' '$2==2{n++} END{print n+0}')"
  c3="$(printf '%s\n' "$eval_rows" | awk -F'|' '$2==3{n++} END{print n+0}')"
  c4="$(printf '%s\n' "$eval_rows" | awk -F'|' '$2==4{n++} END{print n+0}')"
  c5="$(printf '%s\n' "$eval_rows" | awk -F'|' '$2==5{n++} END{print n+0}')"
  echo "[parity pulse (auto)]"
  echo "- why_shown=$reason_context"
  echo "- summary: 1:1=$c1 1:2=$c2 1:3=$c3 1:4=$c4 1:5=$c5"
  printf '%s\n' "$eval_rows" | while IFS= read -r row; do
    IFS='|' read -r name code term meaning certainty branch upstream remote_fresh clean_state dirty ahead behind head_eq_upstream <<< "$row"
    if [[ "$code" -ne 1 ]]; then
      echo "- $name: 1:$code $term ($meaning; certainty=$certainty)"
    fi
  done
}

run_quick() {
  local require_fresh="${1:-0}"
  local parity_detail="${2:-0}"
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

  local parity_rows=""
  for r in "${repos[@]}"; do
    local row
    row="$(repo_sync_eval "$ROOT/$r" "$require_fresh")"
    parity_rows+="$row"$'\n'
  done
  parity_rows="$(printf '%s' "$parity_rows" | sed '/^$/d')"
  if [[ "$parity_detail" -eq 1 ]]; then
    echo "[cleanup audit parity]"
    while IFS= read -r row; do
      emit_parity_row "$row" "explicit cleanup audit"
    done <<< "$parity_rows"
  else
    emit_parity_pulse_summary "$parity_rows" "auto side signal (no extra checks beyond this run)"
  fi

  echo "[local-workspace queue health]"
  local working=0
  local trash=0
  local pm=0
  local handoff_file_present=0
  [[ -d "$ROOT/local-workspace/local-working-files" ]] && working="$(find "$ROOT/local-workspace/local-working-files" -type f | wc -l | tr -d ' ')"
  [[ -d "$ROOT/local-workspace/local-trash-delete" ]] && trash="$(find "$ROOT/local-workspace/local-trash-delete" -type f | wc -l | tr -d ' ')"
  [[ -d "$ROOT/local-workspace/local-cj-pm-only" ]] && pm="$(find "$ROOT/local-workspace/local-cj-pm-only" -type f | wc -l | tr -d ' ')"
  [[ -f "$ROOT/local-workspace/.handoff" ]] && handoff_file_present=1
  echo "- working_files=$working"
  echo "- trash_files=$trash"
  echo "- handoff_file_present=$handoff_file_present"
  echo "- pm_only_files=$pm"

  echo "[soft purge signals]"
  local trash_pending=0
  local trash_pending_days=14
  [[ -d "$ROOT/local-workspace/local-trash-delete" ]] && trash_pending="$(find "$ROOT/local-workspace/local-trash-delete" -type f -mtime +$trash_pending_days | wc -l | tr -d ' ')"
  echo "- trash_soft_purge_pending_files=$trash_pending"
  echo "- trash_soft_purge_threshold_days=$trash_pending_days"
  echo "- trash_soft_purge_mode=SOFT_ONLY (informational, no deletion)"

  echo "[likely duplicates estimate]"
  local tmp_canon="/tmp/audit_ctl_canon_names.txt"
  local tmp_local="/tmp/audit_ctl_local_names.txt"
  find "$ROOT/docs" "$ROOT/bitpod" "$ROOT/bitregime-core" "$ROOT/taylor-runtime" "$ROOT/tools" -type f 2>/dev/null \
    | xargs -I{} basename "{}" | sort -u > "$tmp_canon"
  local local_work_root="$ROOT/local-workspace/local-working-files"
  if [[ -d "$local_work_root" ]]; then
    find "$local_work_root" -type f 2>/dev/null | xargs -I{} basename "{}" | sort -u > "$tmp_local"
  else
    : > "$tmp_local"
  fi
  local likely_dups
  likely_dups="$(comm -12 "$tmp_canon" "$tmp_local" | wc -l | tr -d ' ')"
  echo "- likely_duplicate_filename_count=$likely_dups"

  echo "[workspace naming hygiene]"
  local legacy_bucket_hits
  legacy_bucket_hits="$(find "$ROOT/local-workspace" -type d \( -name 'incoming-clutter' -o -name 'working-files' -o -name 'trash-delete' -o -name 'handoffs' -o -name 'reference-candidates' \) 2>/dev/null | wc -l | tr -d ' ')"
  echo "- legacy_workspace_dir_hits=$legacy_bucket_hits"
  local unexpected_local_children
  unexpected_local_children="$(find "$ROOT/local-workspace" -maxdepth 1 -mindepth 1 -type d -exec basename {} \; | rg -v '^(local-working-files|local-trash-delete|local-cj-pm-only)$' | wc -l | tr -d ' ')"
  echo "- unexpected_local_workspace_children=$unexpected_local_children"
  local non_local_prefix_dirs
  non_local_prefix_dirs="$(find "$ROOT/local-workspace" -mindepth 1 -type d -exec basename {} \; | rg -v '^local-' | wc -l | tr -d ' ')"
  echo "- non_local_prefix_dir_hits=$non_local_prefix_dirs"

  # Stop gate heuristic for quick mode.
  if [[ "$likely_dups" -le 25 && "$legacy_bucket_hits" -eq 0 && "$unexpected_local_children" -eq 0 && "$non_local_prefix_dirs" -eq 0 ]]; then
    echo "quick_gate=STOP_OK"
    return 0
  fi
  echo "quick_gate=ESCALATE_RECOMMENDED"
  return 10
}

run_medium() {
  print_header "T2 Medium"
  local working="$ROOT/local-workspace/local-working-files"
  if [[ ! -d "$working" ]]; then
    echo "medium_note=no local-working-files folder"
    echo "medium_gate=STOP_OK"
    return 0
  fi

  local tmp_in="/tmp/audit_ctl_in_sha.txt"
  local tmp_canon="/tmp/audit_ctl_canon_sha.txt"
  find "$working" -type f -name '*.md' -print0 2>/dev/null | xargs -0 shasum -a 256 | sort > "$tmp_in" || true
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
    run_quick 0 0 || true
    exit 0
  fi

  # T2 or T3 always start with quick.
  local quick_fresh=0
  local quick_parity_detail=1
  [[ "$tier" == "T3" ]] && quick_fresh=1
  if run_quick "$quick_fresh" "$quick_parity_detail"; then
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
