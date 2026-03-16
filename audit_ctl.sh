#!/usr/bin/env bash
set -euo pipefail

ROOT="/Users/cjarguello/bitpod-app"
ZONE_POLICY_FILE="$ROOT/bitpod-tools/config/cleanup_zones_policy.tsv"
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

parity_truth_label() {
  local code="$1"
  local verify="$2"
  case "$code:$verify" in
    1:VERIFIED_FRESH) echo "Verified (99%)" ;;
    2:VERIFIED_LOCAL_ONLY) echo "Verified (72%)" ;;
    2:FETCH_NOT_VERIFIED) echo "Unknown (25%)" ;;
    3:VERIFIED_LOCAL|3:VERIFIED_FRESH) echo "Verified (99%)" ;;
    4:VERIFIED_FRESH) echo "Verified (99%)" ;;
    5:VERIFIED_LOCAL) echo "Verified (95%)" ;;
    *) echo "Unknown (30%)" ;;
  esac
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
    if (cd "$repo_path" && git fetch --all --prune >/dev/null 2>&1); then
      remote_fresh="true"
    else
      remote_fresh="false"
    fi
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

  local code parity meaning verify
  if [[ -z "$upstream" ]]; then
    code=5
    parity="UNLINKED"
    meaning="No upstream is configured"
    verify="VERIFIED_LOCAL"
  elif [[ "$dirty" -gt 0 ]]; then
    code=3
    parity="LOCAL DIVERGED"
    meaning="Local changes exist"
    if [[ "$require_fresh" -eq 1 && "$remote_fresh" == "true" ]]; then
      verify="VERIFIED_FRESH"
    else
      verify="VERIFIED_LOCAL"
    fi
  elif [[ "$require_fresh" -eq 1 && "$remote_fresh" != "true" ]]; then
    code=2
    parity="NOT VERIFIED"
    meaning="Remote refresh failed; fresh parity not established"
    verify="FETCH_NOT_VERIFIED"
  elif [[ "$require_fresh" -eq 1 && "$ahead" -eq 0 && "$behind" -eq 0 && "$head_eq_upstream" == "true" ]]; then
    code=1
    parity="PERFECT"
    meaning="Perfect fresh repo match"
    verify="VERIFIED_FRESH"
  elif [[ "$require_fresh" -eq 1 ]]; then
    code=4
    parity="REMOTE DIVERGED"
    meaning="Upstream mismatch"
    verify="VERIFIED_FRESH"
  else
    code=2
    parity="NOT VERIFIED"
    meaning="Remote not refreshed in this run"
    verify="VERIFIED_LOCAL_ONLY"
  fi

  local clean_state="false"
  local truth_label
  truth_label="$(parity_truth_label "$code" "$verify")"
  [[ "$dirty" -eq 0 ]] && clean_state="true"
  echo "$name|$code|$parity|$meaning|$truth_label|$verify|$branch|${upstream:-none}|$remote_fresh|$clean_state|$dirty|$ahead|$behind|$head_eq_upstream"
}

emit_parity_row() {
  local eval_row="$1"
  local reason_context="$2"
  IFS='|' read -r name code parity meaning truth_label verify branch upstream remote_fresh clean_state dirty ahead behind head_eq_upstream <<< "$eval_row"
  echo "- 1:$code | $name@$branch vs $upstream | $parity - $meaning | truth_label=$truth_label | VERIFY=$verify | EVIDENCE(fetch_fresh=$remote_fresh,clean=$clean_state,dirty_items=$dirty,ahead=$ahead,behind=$behind,head_eq_upstream=$head_eq_upstream) | scope=REPO_PARITY_ONLY | why=$reason_context"
}

emit_overall_parity_line() {
  local eval_rows="$1"
  local require_fresh="${2:-0}"
  local c1 c2 c3 c4 c5 total truth_label verify
  c1="$(printf '%s\n' "$eval_rows" | awk -F'|' '$2==1{n++} END{print n+0}')"
  c2="$(printf '%s\n' "$eval_rows" | awk -F'|' '$2==2{n++} END{print n+0}')"
  c3="$(printf '%s\n' "$eval_rows" | awk -F'|' '$2==3{n++} END{print n+0}')"
  c4="$(printf '%s\n' "$eval_rows" | awk -F'|' '$2==4{n++} END{print n+0}')"
  c5="$(printf '%s\n' "$eval_rows" | awk -F'|' '$2==5{n++} END{print n+0}')"
  total="$(printf '%s\n' "$eval_rows" | sed '/^$/d' | wc -l | tr -d ' ')"

  if [[ "$require_fresh" -eq 1 && "$total" -gt 0 && "$c1" -eq "$total" ]]; then
    echo "- 1:1 | all_repos($total) | PORCELAIN - Perfect fresh all-repo match | truth_label=Verified (99%) | VERIFY=VERIFIED_FRESH | EVIDENCE(perfect_repos=$c1,total_repos=$total)"
    return 0
  fi

  if [[ "$require_fresh" -eq 1 && "$c2" -gt 0 ]]; then
    truth_label="Unknown (25%)"
    verify="FETCH_NOT_VERIFIED"
    echo "- overall | fresh all-repo 1:1 not established in this run | truth_label=$truth_label | VERIFY=$verify | EVIDENCE(summary=1:1=$c1 1:2=$c2 1:3=$c3 1:4=$c4 1:5=$c5,total_repos=$total)"
    return 0
  fi

  if [[ "$require_fresh" -eq 1 ]]; then
    truth_label="Verified (99%)"
    verify="VERIFIED_FRESH"
    echo "- overall | fresh all-repo 1:1 not proven in this run | truth_label=$truth_label | VERIFY=$verify | EVIDENCE(summary=1:1=$c1 1:2=$c2 1:3=$c3 1:4=$c4 1:5=$c5,total_repos=$total)"
    return 0
  fi

  echo "- overall | fresh all-repo 1:1 not checked in this run | truth_label=Verified (72%) | VERIFY=VERIFIED_LOCAL_ONLY | EVIDENCE(summary=1:1=$c1 1:2=$c2 1:3=$c3 1:4=$c4 1:5=$c5,total_repos=$total)"
}

emit_parity_pulse_summary() {
  local eval_rows="$1"
  local reason_context="$2"
  local require_fresh="${3:-0}"
  local c1 c2 c3 c4 c5
  c1="$(printf '%s\n' "$eval_rows" | awk -F'|' '$2==1{n++} END{print n+0}')"
  c2="$(printf '%s\n' "$eval_rows" | awk -F'|' '$2==2{n++} END{print n+0}')"
  c3="$(printf '%s\n' "$eval_rows" | awk -F'|' '$2==3{n++} END{print n+0}')"
  c4="$(printf '%s\n' "$eval_rows" | awk -F'|' '$2==4{n++} END{print n+0}')"
  c5="$(printf '%s\n' "$eval_rows" | awk -F'|' '$2==5{n++} END{print n+0}')"
  echo "[parity pulse (auto)]"
  echo "- why_shown=$reason_context"
  echo "- scope=REPO_PARITY_ONLY"
  echo "- summary: 1:1=$c1 1:2=$c2 1:3=$c3 1:4=$c4 1:5=$c5"
  emit_overall_parity_line "$eval_rows" "$require_fresh"
  printf '%s\n' "$eval_rows" | while IFS= read -r row; do
    IFS='|' read -r name code parity meaning truth_label verify branch upstream remote_fresh clean_state dirty ahead behind head_eq_upstream <<< "$row"
    if [[ "$code" -ne 1 ]]; then
      emit_parity_row "$row" "auto parity pulse"
    fi
  done
}

collect_repo_paths() {
  local out=()
  local path
  for path in "$ROOT"/*; do
    [[ -d "$path/.git" ]] || continue
    out+=("$(basename "$path")")
  done
  if [[ "${#out[@]}" -eq 0 ]]; then
    return 0
  fi
  printf '%s\n' "${out[@]}" | sort
}

emit_managed_zones_summary() {
  echo "[managed folder zones]"
  if [[ ! -f "$ZONE_POLICY_FILE" ]]; then
    echo "- zone_policy_file=MISSING path=$ZONE_POLICY_FILE"
    return 0
  fi
  local lines=0
  while IFS='|' read -r zone mode rel_path notes; do
    [[ -z "${zone// }" ]] && continue
    [[ "$zone" =~ ^# ]] && continue
    lines=$((lines + 1))
    local abs_path="$ROOT/$rel_path"
    if [[ ! -d "$abs_path" ]]; then
      echo "- zone=$zone mode=$mode path=$rel_path status=MISSING notes=${notes:-none}"
      continue
    fi

    local file_count dup_names large_files
    file_count="$(find "$abs_path" -type f 2>/dev/null | wc -l | tr -d ' ')"
    dup_names="$(find "$abs_path" -type f -exec basename {} \; 2>/dev/null | sort | uniq -d | wc -l | tr -d ' ')"
    large_files="$(find "$abs_path" -type f -size +10M 2>/dev/null | wc -l | tr -d ' ')"
    echo "- zone=$zone mode=$mode path=$rel_path files=$file_count dup_names=$dup_names large_files_gt10mb=$large_files notes=${notes:-none}"
  done < "$ZONE_POLICY_FILE"
  if [[ "$lines" -eq 0 ]]; then
    echo "- zone_policy_entries=0 (file exists but has no active rows)"
  fi
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
  local repos=()
  while IFS= read -r repo_name; do
    [[ -n "$repo_name" ]] && repos+=("$repo_name")
  done < <(collect_repo_paths)
  if [[ "${#repos[@]}" -eq 0 ]]; then
    echo "- repo_scan_status=NO_GIT_REPOS_FOUND_UNDER_ROOT"
  fi
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
    local p1 p2 p3 p4 p5
    p1="$(printf '%s\n' "$parity_rows" | awk -F'|' '$2==1{n++} END{print n+0}')"
    p2="$(printf '%s\n' "$parity_rows" | awk -F'|' '$2==2{n++} END{print n+0}')"
    p3="$(printf '%s\n' "$parity_rows" | awk -F'|' '$2==3{n++} END{print n+0}')"
    p4="$(printf '%s\n' "$parity_rows" | awk -F'|' '$2==4{n++} END{print n+0}')"
    p5="$(printf '%s\n' "$parity_rows" | awk -F'|' '$2==5{n++} END{print n+0}')"
    echo "- summary: 1:1=$p1 1:2=$p2 1:3=$p3 1:4=$p4 1:5=$p5"
    emit_overall_parity_line "$parity_rows" "$require_fresh"
    while IFS= read -r row; do
      emit_parity_row "$row" "explicit cleanup audit"
    done <<< "$parity_rows"
  else
    emit_parity_pulse_summary "$parity_rows" "auto side signal (no extra checks beyond this run)" "$require_fresh"
  fi

  echo "[local-workspace queue health]"
  local working=0
  local trash=0
  local pm=0
  local codex=0
  local handoff_files=0
  [[ -d "$ROOT/local-workspace/local-working-files" ]] && working="$(find "$ROOT/local-workspace/local-working-files" -type f | wc -l | tr -d ' ')"
  [[ -d "$ROOT/local-workspace/local-trash-delete" ]] && trash="$(find "$ROOT/local-workspace/local-trash-delete" -type f | wc -l | tr -d ' ')"
  [[ -d "$ROOT/local-workspace/local-cj-pm-only" ]] && pm="$(find "$ROOT/local-workspace/local-cj-pm-only" -type f | wc -l | tr -d ' ')"
  [[ -d "$ROOT/local-workspace/local-codex" ]] && codex="$(find "$ROOT/local-workspace/local-codex" -type f | wc -l | tr -d ' ')"
  [[ -d "$ROOT/local-workspace/local-handoffs" ]] && handoff_files="$(find "$ROOT/local-workspace/local-handoffs" -type f | wc -l | tr -d ' ')"
  echo "- working_files=$working"
  echo "- trash_files=$trash"
  echo "- handoff_files=$handoff_files"
  echo "- pm_only_files=$pm"
  echo "- codex_state_files=$codex"

  emit_managed_zones_summary

  echo "[soft purge signals]"
  local trash_pending=0
  local trash_pending_days=14
  [[ -d "$ROOT/local-workspace/local-trash-delete" ]] && trash_pending="$(find "$ROOT/local-workspace/local-trash-delete" -type f -mtime +$trash_pending_days | wc -l | tr -d ' ')"
  echo "- trash_soft_purge_pending_files=$trash_pending"
  echo "- trash_soft_purge_threshold_days=$trash_pending_days"
  echo "- trash_soft_purge_mode=SOFT_ONLY (high-certainty purge-candidate review signal only; no deletion)"
  echo "- trash_soft_purge_next_action=review_for_promotion_from_quarantine_to_local_purge_or_keep_in_quarantine"

  echo "[likely duplicates estimate]"
  local tmp_canon="/tmp/audit_ctl_canon_names.txt"
  local tmp_local="/tmp/audit_ctl_local_names.txt"
  local canon_scan_dirs=()
  local maybe_dirs=(
    "$ROOT/bitpod"
    "$ROOT/bitregime-core"
    "$ROOT/bitpod-docs"
    "$ROOT/bitpod-tools"
    "$ROOT/bitpod-taylor-runtime"
    "$ROOT/docs"
    "$ROOT/tools"
    "$ROOT/taylor-runtime"
    "$ROOT/local-workspace/local-codex"
  )
  local d
  for d in "${maybe_dirs[@]}"; do
    [[ -d "$d" ]] && canon_scan_dirs+=("$d")
  done
  if [[ "${#canon_scan_dirs[@]}" -gt 0 ]]; then
    find "${canon_scan_dirs[@]}" \
      \( -path '*/.git' -o -path '*/.git/*' \) -prune -o \
      -type f ! -name '.DS_Store' -print 2>/dev/null | \
      xargs -I{} basename "{}" | sort -u > "$tmp_canon"
  else
    : > "$tmp_canon"
  fi
  local local_work_root="$ROOT/local-workspace/local-working-files"
  if [[ -d "$local_work_root" ]]; then
    find "$local_work_root" \
      \( -path '*/.git' -o -path '*/.git/*' \) -prune -o \
      -type f ! -name '.DS_Store' -print 2>/dev/null | \
      xargs -I{} basename "{}" | sort -u > "$tmp_local"
  else
    : > "$tmp_local"
  fi
  local likely_dups
  likely_dups="$(comm -12 "$tmp_canon" "$tmp_local" | wc -l | tr -d ' ')"
  echo "- likely_duplicate_filename_count=$likely_dups"

  echo "[workspace naming hygiene]"
  local hygiene_roots=()
  [[ -d "$ROOT/local-workspace/local-working-files" ]] && hygiene_roots+=("$ROOT/local-workspace/local-working-files")
  [[ -d "$ROOT/local-workspace/local-handoffs" ]] && hygiene_roots+=("$ROOT/local-workspace/local-handoffs")
  local legacy_bucket_hits=0
  if [[ "${#hygiene_roots[@]}" -gt 0 ]]; then
    legacy_bucket_hits="$(find "${hygiene_roots[@]}" -type d \( -name 'incoming-clutter' -o -name 'working-files' -o -name 'trash-delete' -o -name 'handoffs' -o -name 'reference-candidates' \) 2>/dev/null | wc -l | tr -d ' ')"
  fi
  echo "- active_legacy_bucket_hits=$legacy_bucket_hits"
  local unexpected_local_children
  unexpected_local_children="$(find "$ROOT/local-workspace" -maxdepth 1 -mindepth 1 -type d -exec basename {} \; | rg -v '^(local-working-files|local-handoffs|local-trash-delete|local-cj-pm-only|local-codex)$' | wc -l | tr -d ' ')"
  echo "- unexpected_local_workspace_children=$unexpected_local_children"

  # Stop gate heuristic for quick mode.
  if [[ "$likely_dups" -le 25 && "$legacy_bucket_hits" -eq 0 && "$unexpected_local_children" -eq 0 ]]; then
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
  local canon_scan_dirs=()
  local maybe_dirs=(
    "$ROOT/bitpod"
    "$ROOT/bitregime-core"
    "$ROOT/bitpod-docs"
    "$ROOT/bitpod-tools"
    "$ROOT/bitpod-taylor-runtime"
    "$ROOT/docs"
    "$ROOT/tools"
    "$ROOT/taylor-runtime"
    "$ROOT/local-workspace/local-codex"
  )
  local d
  for d in "${maybe_dirs[@]}"; do
    [[ -d "$d" ]] && canon_scan_dirs+=("$d")
  done
  if [[ "${#canon_scan_dirs[@]}" -gt 0 ]]; then
    find "${canon_scan_dirs[@]}" -type f -name '*.md' -print0 2>/dev/null | xargs -0 shasum -a 256 | sort > "$tmp_canon" || true
  else
    : > "$tmp_canon"
  fi

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
  emit_managed_zones_summary
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
    run_quick 0 1 || true
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
        echo "t3_scope_notice=repo parity verified; medium/full tiers not executed"
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
        echo "t3_scope_notice=repo parity + medium checks executed; full tier not executed"
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
