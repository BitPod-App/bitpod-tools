#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEFAULT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
ROOT="${BITPOD_APP_ROOT:-${WORKSPACE:-$DEFAULT_ROOT}}"
REGISTRY_FILE="${BITPOD_REPO_REGISTRY_FILE:-$ROOT/bitpod-tools/config/repo_registry.tsv}"
ZONE_POLICY_FILE="${BITPOD_CLEANUP_ZONE_POLICY_FILE:-$ROOT/bitpod-tools/config/cleanup_zones_policy.tsv}"
LOCAL_WORKSPACE_CONTRACT_FILE="${BITPOD_LOCAL_WORKSPACE_CONTRACT_FILE:-$ROOT/bitpod-docs/process/local-workspace-skeleton-contract.toml}"
LOCAL_WORKSPACE_PROFILE="${BITPOD_LOCAL_WORKSPACE_PROFILE:-personal_machine_full}"
NOW="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
TMP_DIR="$(mktemp -d "${TMPDIR:-/tmp}/audit_ctl.XXXXXX")"
trap 'rm -rf "$TMP_DIR"' EXIT

REGISTRY_PROBLEMS_FILE="$TMP_DIR/registry_problems.txt"
ZONE_ROWS_FILE="$TMP_DIR/zone_rows.txt"
TRASH_BUCKET_ROWS_FILE="$TMP_DIR/trash_bucket_rows.txt"
CLEANUP_PLAN_ROWS_FILE="$TMP_DIR/cleanup_plan_rows.txt"
DUPLICATE_ROWS_FILE="$TMP_DIR/duplicate_rows.txt"
REPO_TEMPORAL_ROWS_FILE="$TMP_DIR/repo_temporal_rows.txt"
TMP_CANON_NAMES="$TMP_DIR/canon_names.txt"
TMP_LOCAL_NAMES="$TMP_DIR/local_names.txt"
TMP_IN_SHA="$TMP_DIR/in_sha.txt"
TMP_CANON_SHA="$TMP_DIR/canon_sha.txt"
STALE_BRANCH_ROWS_FILE="$TMP_DIR/stale_branch_rows.txt"
OPEN_PR_ROWS_FILE="$TMP_DIR/open_pr_rows.txt"

NETWORK_TIMEOUT_SECONDS="${BITPOD_AUDIT_NETWORK_TIMEOUT_SECONDS:-15}"
TRASH_BUCKET_ACTION_FILE_THRESHOLD="${BITPOD_TRASH_BUCKET_ACTION_FILE_THRESHOLD:-100}"
LOCAL_TRASH_PURGE_DAYS="${BITPOD_LOCAL_TRASH_PURGE_DAYS:-30}"
LOCAL_PURGE_OS_TRASH_DAYS="${BITPOD_LOCAL_PURGE_OS_TRASH_DAYS:-30}"
LOCAL_PURGE_OS_TRASH_ALLOWED="${BITPOD_LOCAL_PURGE_OS_TRASH_ALLOWED:-0}"

repo_rows=""
repo_total=0
code1=0
code2=0
code3=0
code4=0
code5=0
pulse_matched=0
pulse_local_diverged=0
pulse_remote_mismatch=0
pulse_unlinked=0
cleanup_likely_match=0
cleanup_local_diverged=0
cleanup_remote_mismatch=0
cleanup_unlinked=0
repo_fetch_failed=0
repo_verified_count=0
repo_not_verified_count=0
registry_problem_count=0
registry_problem_lines=""
working_files=0
trash_files=0
handoff_files=0
pm_only_files=0
codex_state_files=0
shared_dropoff_files=0
trash_soft_purge_pending_files=0
trash_soft_purge_threshold_days="$LOCAL_TRASH_PURGE_DAYS"
trash_root_bucket_count=0
trash_actionable_bucket_count=0
cleanup_plan_move_to_trash_files=0
cleanup_plan_move_to_purge_files=0
cleanup_plan_os_trash_candidate_files=0
cleanup_plan_report_only_files=0
cleanup_plan_execution_allowed_count=0
cleanup_plan_row_count=0
local_purge_os_trash_candidate_files=0
repo_temporal_candidate_count=0
repo_temporal_candidate_files=0
likely_duplicate_filename_count=0
active_legacy_bucket_hits=0
unexpected_local_workspace_children=0
non_local_prefix_direct_children=0
scanned_reference_md=0
exact_duplicate_md=0
dir_count_depth2=0
file_count_depth2=0
strict_canonical_zone_issues=0
report_only_zone_count=0
strict_zone_count=0
stale_local_branch_count=0
stale_remote_branch_count=0
open_pr_count=0
network_probe_fail_count=0
network_probe_rows=""
stale_branch_rows=""
open_pr_rows=""
contract_required_paths=""
contract_optional_paths=""
contract_disabled_paths=""
contract_allowed_direct_children=""
contract_profile_loaded=0

normalize() {
  tr '[:upper:]' '[:lower:]'
}

has_phrase() {
  local haystack="$1"
  local needle="$2"
  [[ "$haystack" == *"$needle"* ]]
}

print_header() {
  echo "Audit Control | $1"
  echo "Timestamp: $NOW"
}

print_section() {
  echo
  echo "$1"
}

render_bool() {
  if [[ "$1" -eq 1 ]]; then
    echo "YES"
  else
    echo "NO"
  fi
}

run_with_timeout() {
  local timeout_seconds="$1"
  shift

  python3 - "$timeout_seconds" "$@" <<'PY'
import subprocess
import sys

timeout = int(sys.argv[1])
cmd = sys.argv[2:]
try:
    completed = subprocess.run(cmd, timeout=timeout, capture_output=True, text=True)
    sys.stdout.write(completed.stdout)
    sys.stderr.write(completed.stderr)
    raise SystemExit(completed.returncode)
except subprocess.TimeoutExpired as exc:
    if exc.stdout:
        sys.stdout.write(exc.stdout)
    if exc.stderr:
        sys.stderr.write(exc.stderr)
    raise SystemExit(124)
PY
}

append_network_probe_failure() {
  local surface="$1"
  local repo="$2"
  local operation="$3"
  local detail="$4"
  network_probe_fail_count=$((network_probe_fail_count + 1))
  network_probe_rows+="$surface|$repo|$operation|$detail"$'\n'
}

load_local_workspace_contract() {
  [[ "$contract_profile_loaded" -eq 1 ]] && return 0

  local contract_output=""
  contract_output="$(
    python3 - "$LOCAL_WORKSPACE_CONTRACT_FILE" "$LOCAL_WORKSPACE_PROFILE" <<'PY'
import shlex
import sys

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

contract_path = sys.argv[1]
profile = sys.argv[2]

with open(contract_path, "rb") as fh:
    data = tomllib.load(fh)

profiles = data.get("profiles", {})
aliases = data.get("profile_aliases", {})
profile = aliases.get(profile, profile)
if profile not in profiles:
    raise SystemExit(f"profile not found in contract: {profile}")

profile_data = profiles[profile]
required = profile_data.get("required_paths", [])
optional = profile_data.get("optional_paths", [])
disabled = profile_data.get("disabled_paths", [])
allowed_direct_children = sorted({path.split("/", 1)[0] for path in required + optional})

def emit(name: str, value: str) -> None:
    print(f"{name}={shlex.quote(value)}")

emit("contract_required_paths", "\n".join(required))
emit("contract_optional_paths", "\n".join(optional))
emit("contract_disabled_paths", "\n".join(disabled))
emit("contract_allowed_direct_children", "\n".join(allowed_direct_children))
PY
  )" || {
    echo "[audit_ctl] failed to load local-workspace contract: $LOCAL_WORKSPACE_CONTRACT_FILE (profile=$LOCAL_WORKSPACE_PROFILE)" >&2
    return 1
  }

  eval "$contract_output"
  contract_profile_loaded=1
}

path_list_contains() {
  local list="$1"
  local needle="$2"
  local item
  while IFS= read -r item; do
    [[ -z "$item" ]] && continue
    if [[ "$item" == "$needle" ]]; then
      return 0
    fi
  done <<< "$list"
  return 1
}

assert_registry_ready() {
  if [[ ! -f "$REGISTRY_FILE" ]]; then
    echo "[audit_ctl] repo registry missing: $REGISTRY_FILE" >&2
    return 1
  fi
  return 0
}

collect_repo_paths() {
  local feature="$1"
  local rows=0
  : > "$REGISTRY_PROBLEMS_FILE"

  while IFS='|' read -r repo rel_path pulse_enabled cleanup_enabled thread_visible verified notes; do
    [[ -z "${repo// }" ]] && continue
    [[ "$repo" =~ ^# ]] && continue
    rows=$((rows + 1))

    local feature_flag=0
    if [[ "$feature" == "pulse" ]]; then
      feature_flag="${pulse_enabled:-0}"
    else
      feature_flag="${cleanup_enabled:-0}"
    fi
    [[ "$feature_flag" == "1" ]] || continue

    if [[ "${verified:-0}" != "1" ]]; then
      echo "$repo|UNVERIFIED_REGISTRY|${notes:-verification pending}" >> "$REGISTRY_PROBLEMS_FILE"
      continue
    fi

    local abs_path="$ROOT/$rel_path"
    if [[ ! -d "$abs_path" ]]; then
      echo "$repo|MISSING_PATH|$rel_path" >> "$REGISTRY_PROBLEMS_FILE"
      continue
    fi
    if [[ ! -d "$abs_path/.git" ]]; then
      echo "$repo|NOT_GIT_REPO|$rel_path" >> "$REGISTRY_PROBLEMS_FILE"
      continue
    fi

    printf '%s\n' "$abs_path"
  done < "$REGISTRY_FILE"

  if [[ "$rows" -eq 0 ]]; then
    echo "__EMPTY_REGISTRY__"
  fi
}

repo_sync_eval() {
  local repo_path="$1"
  local require_fresh="$2"
  local name branch upstream dirty ahead behind head_sha upstream_sha head_eq_upstream remote_fresh
  name="$(basename "$repo_path")"
  branch="$(cd "$repo_path" && git rev-parse --abbrev-ref HEAD)"
  upstream="$(cd "$repo_path" && git for-each-ref --format='%(upstream:short)' "refs/heads/$branch" | head -n1)"
  dirty="$(cd "$repo_path" && git status --porcelain | wc -l | tr -d ' ')"
  ahead=0
  behind=0
  head_sha="$(cd "$repo_path" && git rev-parse HEAD)"
  upstream_sha=""
  head_eq_upstream="unknown"
  remote_fresh="false"

  if [[ "$require_fresh" -eq 1 ]]; then
    if (cd "$repo_path" && run_with_timeout "$NETWORK_TIMEOUT_SECONDS" git fetch --all --prune >/dev/null 2>&1); then
      remote_fresh="true"
    else
      fetch_status=$?
      if [[ "$fetch_status" -eq 124 ]]; then
        append_network_probe_failure "repo_parity" "$name" "git_fetch" "timed out after ${NETWORK_TIMEOUT_SECONDS}s"
      fi
    fi
  fi

  if [[ -n "$upstream" ]] && (cd "$repo_path" && git rev-parse --verify --quiet "$upstream^{commit}" >/dev/null); then
    local ab
    ab="$(cd "$repo_path" && git rev-list --left-right --count "HEAD...$upstream")"
    ahead="$(printf '%s' "$ab" | awk '{print $1}')"
    behind="$(printf '%s' "$ab" | awk '{print $2}')"
    upstream_sha="$(cd "$repo_path" && git rev-parse "$upstream")"
    if [[ "$head_sha" == "$upstream_sha" ]]; then
      head_eq_upstream="true"
    else
      head_eq_upstream="false"
    fi
  elif [[ -n "$upstream" ]]; then
    upstream=""
  fi

  local code status_key verification verification_detail meaning
  if [[ -z "$upstream" ]]; then
    code=5
    status_key="UNLINKED"
    verification="VERIFIED"
    verification_detail="Verified locally: no upstream configured."
    meaning="No upstream is configured"
  elif [[ "$dirty" -gt 0 ]]; then
    code=3
    status_key="LOCAL_DIVERGED"
    verification="VERIFIED"
    verification_detail="Verified locally: uncommitted or untracked changes exist."
    meaning="Local changes exist"
  elif [[ "$require_fresh" -eq 1 && "$remote_fresh" != "true" ]]; then
    code=2
    status_key="LIKELY_MATCH"
    verification="NOT VERIFIED"
    verification_detail="Fresh remote verification failed; local state suggests a likely match, not guaranteed."
    meaning="Remote refresh failed; fresh parity not established"
  elif [[ "$require_fresh" -eq 1 && "$ahead" -eq 0 && "$behind" -eq 0 && "$head_eq_upstream" == "true" ]]; then
    code=1
    status_key="MATCHED"
    verification="VERIFIED"
    verification_detail="Fresh remote verification succeeded."
    meaning="Perfect fresh repo match"
  elif [[ "$require_fresh" -eq 1 ]]; then
    code=4
    status_key="REMOTE_MISMATCH"
    verification="VERIFIED"
    verification_detail="Fresh remote verification succeeded."
    meaning="Upstream mismatch"
  else
    code=2
    status_key="LIKELY_MATCH"
    verification="NOT VERIFIED"
    verification_detail="Fresh remote verification was not run; local state suggests a likely match, not guaranteed."
    meaning="Remote not refreshed in this run"
  fi

  echo "$name|$code|$status_key|$verification|$verification_detail|$meaning|$branch|${upstream:-none}|$remote_fresh|$dirty|$ahead|$behind|$head_eq_upstream"
}

build_repo_rows() {
  local feature="$1"
  local require_fresh="$2"
  local paths_output
  paths_output="$(collect_repo_paths "$feature")"

  if [[ "$paths_output" == "__EMPTY_REGISTRY__" ]]; then
    echo "[audit_ctl] repo registry has no active rows: $REGISTRY_FILE" >&2
    return 1
  fi

  repo_rows=""
  while IFS= read -r repo_path; do
    [[ -z "$repo_path" ]] && continue
    local row
    row="$(repo_sync_eval "$repo_path" "$require_fresh")"
    repo_rows+="$row"$'\n'
  done <<< "$paths_output"
  repo_rows="$(printf '%s' "$repo_rows" | sed '/^$/d')"
  return 0
}

count_code() {
  local rows="$1"
  local code="$2"
  printf '%s\n' "$rows" | awk -F'|' -v code="$code" '$2==code{n++} END{print n+0}'
}

count_status() {
  local rows="$1"
  local status_key="$2"
  printf '%s\n' "$rows" | awk -F'|' -v key="$status_key" '$3==key{n++} END{print n+0}'
}

count_verification() {
  local rows="$1"
  local verification="$2"
  printf '%s\n' "$rows" | awk -F'|' -v key="$verification" '$4==key{n++} END{print n+0}'
}

summarize_repo_rows() {
  code1="$(count_code "$repo_rows" 1)"
  code2="$(count_code "$repo_rows" 2)"
  code3="$(count_code "$repo_rows" 3)"
  code4="$(count_code "$repo_rows" 4)"
  code5="$(count_code "$repo_rows" 5)"
  repo_total="$(printf '%s\n' "$repo_rows" | sed '/^$/d' | wc -l | tr -d ' ')"
  repo_verified_count="$(count_verification "$repo_rows" VERIFIED)"
  repo_not_verified_count="$(count_verification "$repo_rows" "NOT VERIFIED")"
  repo_fetch_failed="$(printf '%s\n' "$repo_rows" | awk -F'|' '$5 ~ /Fresh remote verification failed/{n++} END{print n+0}')"
  pulse_matched=$((code1 + code2))
  pulse_local_diverged="$code3"
  pulse_remote_mismatch="$code4"
  pulse_unlinked="$code5"
  cleanup_likely_match=$((code1 + code2))
  cleanup_local_diverged="$code3"
  cleanup_remote_mismatch="$code4"
  cleanup_unlinked="$code5"
}

pulse_label_for_code() {
  case "$1" in
    1|2) echo "MATCHED" ;;
    3) echo "LOCAL DIVERGED" ;;
    4) echo "REMOTE MISMATCH" ;;
    5) echo "UNLINKED" ;;
    *) echo "UNKNOWN" ;;
  esac
}

cleanup_label_for_code() {
  case "$1" in
    1|2) echo "LIKELY MATCH" ;;
    3) echo "LOCAL DIVERGED" ;;
    4) echo "REMOTE MISMATCH" ;;
    5) echo "UNLINKED" ;;
    *) echo "UNKNOWN" ;;
  esac
}

collect_registry_problems() {
  registry_problem_count=0
  registry_problem_lines=""
  if [[ -f "$REGISTRY_PROBLEMS_FILE" ]]; then
    registry_problem_count="$(wc -l < "$REGISTRY_PROBLEMS_FILE" | tr -d ' ')"
    registry_problem_lines="$(cat "$REGISTRY_PROBLEMS_FILE")"
  fi
}

count_files() {
  local path="$1"
  if [[ -d "$path" ]]; then
    find "$path" -type f 2>/dev/null | wc -l | tr -d ' '
  else
    echo "0"
  fi
}

count_dirs() {
  local path="$1"
  if [[ -d "$path" ]]; then
    find "$path" -type d 2>/dev/null | wc -l | tr -d ' '
  else
    echo "0"
  fi
}

append_cleanup_plan_row() {
  local finding_id="$1"
  local scope="$2"
  local action="$3"
  local path="$4"
  local destination="$5"
  local reason="$6"
  local policy_rule="$7"
  local file_count="$8"
  local dir_count="$9"
  local execution_allowed="${10}"
  local requires_tier="${11}"
  local requires_permission="${12}"

  cleanup_plan_row_count=$((cleanup_plan_row_count + 1))
  if [[ "$execution_allowed" == "true" ]]; then
    cleanup_plan_execution_allowed_count=$((cleanup_plan_execution_allowed_count + 1))
  fi
  case "$action" in
    soft_move_to_trash)
      cleanup_plan_move_to_trash_files=$((cleanup_plan_move_to_trash_files + file_count))
      ;;
    move_to_local_purge)
      cleanup_plan_move_to_purge_files=$((cleanup_plan_move_to_purge_files + file_count))
      ;;
    os_trash_candidate)
      cleanup_plan_os_trash_candidate_files=$((cleanup_plan_os_trash_candidate_files + file_count))
      ;;
    report_only)
      cleanup_plan_report_only_files=$((cleanup_plan_report_only_files + file_count))
      ;;
  esac

  printf '%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s\n' \
    "$finding_id" "$scope" "$action" "$path" "$destination" "$reason" "$policy_rule" "$file_count" "$dir_count" "$execution_allowed" "$requires_tier" "$requires_permission" >> "$CLEANUP_PLAN_ROWS_FILE"
}

is_generic_duplicate_name() {
  case "$1" in
    README.md|index.html)
      return 0
      ;;
    *)
      return 1
      ;;
  esac
}

collect_queue_health() {
  load_local_workspace_contract
  working_files="$(count_files "$ROOT/local-workspace/local-working-files")"
  trash_files="$(count_files "$ROOT/local-workspace/local-trash-delete")"
  handoff_files="$(count_files "$ROOT/local-workspace/local-handoffs")"
  pm_only_files="$(count_files "$ROOT/local-workspace/local-personal-only")"
  if [[ "$pm_only_files" -eq 0 ]]; then
    pm_only_files="$(count_files "$ROOT/local-workspace/local-cj-pm-only")"
  fi
  codex_state_files="$(count_files "$ROOT/local-workspace/local-codex")"
  shared_dropoff_files="$(count_files "$ROOT/local-workspace/local-shared-dropoff")"
}

collect_likely_duplicate_names() {
  : > "$TMP_CANON_NAMES"
  : > "$TMP_LOCAL_NAMES"
  : > "$DUPLICATE_ROWS_FILE"

  local canon_dirs=()
  while IFS='|' read -r repo rel_path pulse_enabled cleanup_enabled thread_visible verified notes; do
    [[ -z "${repo// }" ]] && continue
    [[ "$repo" =~ ^# ]] && continue
    [[ "${cleanup_enabled:-0}" == "1" ]] || continue
    [[ "${verified:-0}" == "1" ]] || continue
    if [[ -d "$ROOT/$rel_path" ]]; then
      canon_dirs+=("$ROOT/$rel_path")
    fi
  done < "$REGISTRY_FILE"

  if [[ "${#canon_dirs[@]}" -gt 0 ]]; then
    find "${canon_dirs[@]}" \
      \( -path '*/.git' -o -path '*/.git/*' \) -prune -o \
      -type f ! -name '.DS_Store' -print 2>/dev/null | \
      while IFS= read -r path; do
        name="${path##*/}"
        is_generic_duplicate_name "$name" && continue
        printf '%s\n' "$name"
      done | sort -u > "$TMP_CANON_NAMES" || true
  fi

  if [[ -d "$ROOT/local-workspace/local-working-files" ]]; then
    find "$ROOT/local-workspace/local-working-files" \
      \( -path '*/.git' -o -path '*/.git/*' \) -prune -o \
      -type f ! -name '.DS_Store' -print 2>/dev/null | \
      while IFS= read -r path; do
        name="${path##*/}"
        is_generic_duplicate_name "$name" && continue
        printf '%s\n' "$name"
      done | sort -u > "$TMP_LOCAL_NAMES" || true
  fi

  likely_duplicate_filename_count="$(comm -12 "$TMP_CANON_NAMES" "$TMP_LOCAL_NAMES" | wc -l | tr -d ' ')"
  comm -12 "$TMP_CANON_NAMES" "$TMP_LOCAL_NAMES" | while IFS= read -r name; do
    [[ -z "$name" ]] && continue
    local local_matches=0
    local canon_matches=0
    local_matches="$(find "$ROOT/local-workspace/local-working-files" \
      \( -path '*/.git' -o -path '*/.git/*' \) -prune -o \
      -type f -name "$name" -print 2>/dev/null | wc -l | tr -d ' ')"
    canon_matches="$(find "${canon_dirs[@]}" \
      \( -path '*/.git' -o -path '*/.git/*' \) -prune -o \
      -type f -name "$name" -print 2>/dev/null | wc -l | tr -d ' ')"
    echo "$name|$local_matches|$canon_matches" >> "$DUPLICATE_ROWS_FILE"
  done
}

collect_workspace_hygiene() {
  load_local_workspace_contract
  collect_likely_duplicate_names
  collect_trash_bucket_actionability
  local legacy_scan_dirs=()
  if [[ -d "$ROOT/local-workspace/local-working-files" ]]; then
    legacy_scan_dirs+=("$ROOT/local-workspace/local-working-files")
  fi
  if path_list_contains "$contract_allowed_direct_children" "local-shared-dropoff" && [[ -d "$ROOT/local-workspace/local-shared-dropoff" ]]; then
    legacy_scan_dirs+=("$ROOT/local-workspace/local-shared-dropoff")
  fi

  if [[ "${#legacy_scan_dirs[@]}" -gt 0 ]]; then
    active_legacy_bucket_hits="$(
      find \
        "${legacy_scan_dirs[@]}" \
        -type d \
        \( -name 'incoming-clutter' -o -name 'working-files' -o -name 'trash-delete' -o -name 'handoffs' -o -name 'reference-candidates' \) \
        2>/dev/null | wc -l | tr -d ' '
    )"
  else
    active_legacy_bucket_hits=0
  fi

  if [[ -d "$ROOT/local-workspace" ]]; then
    unexpected_local_workspace_children=0
    local child_name=""
    while IFS= read -r child_name; do
      [[ -z "$child_name" ]] && continue
      if ! path_list_contains "$contract_allowed_direct_children" "$child_name"; then
        unexpected_local_workspace_children=$((unexpected_local_workspace_children + 1))
      fi
    done < <(find "$ROOT/local-workspace" -maxdepth 1 -mindepth 1 -type d -exec basename {} \; 2>/dev/null)
    non_local_prefix_direct_children="$(
      find "$ROOT/local-workspace" -maxdepth 1 -mindepth 1 -type d -exec basename {} \; 2>/dev/null | \
      awk '!/^local-/ {n++} END{print n+0}'
    )"
    trash_soft_purge_pending_files="$(
      find "$ROOT/local-workspace/local-trash-delete" -type f -mtime +"$trash_soft_purge_threshold_days" 2>/dev/null | \
      wc -l | tr -d ' '
    )"
  else
    unexpected_local_workspace_children=0
    non_local_prefix_direct_children=0
    trash_soft_purge_pending_files=0
  fi
}

collect_trash_bucket_actionability() {
  : > "$TRASH_BUCKET_ROWS_FILE"
  trash_root_bucket_count=0
  trash_actionable_bucket_count=0

  local trash_root="$ROOT/local-workspace/local-trash-delete"
  [[ -d "$trash_root" ]] || return 0

  local bucket
  while IFS= read -r bucket; do
    [[ -z "$bucket" ]] && continue
    local name="${bucket##*/}"
    [[ "$name" == "local-purge" ]] && continue

    trash_root_bucket_count=$((trash_root_bucket_count + 1))
    local rel_path="local-workspace/local-trash-delete/$name"
    local file_count=0
    local dir_count=0
    local stale_files=0
    local has_git=0
    local action="review"

    file_count="$(find "$bucket" -type f 2>/dev/null | wc -l | tr -d ' ')"
    dir_count="$(find "$bucket" -type d 2>/dev/null | wc -l | tr -d ' ')"
    stale_files="$(find "$bucket" -type f -mtime +"$trash_soft_purge_threshold_days" 2>/dev/null | wc -l | tr -d ' ')"
    [[ -d "$bucket/.git" ]] && has_git=1

    if [[ "$file_count" -ge "$TRASH_BUCKET_ACTION_FILE_THRESHOLD" || "$stale_files" -gt 0 || "$has_git" -eq 1 ]]; then
      action="review_for_local_purge"
      trash_actionable_bucket_count=$((trash_actionable_bucket_count + 1))
    fi

    echo "$rel_path|$file_count|$dir_count|$stale_files|$has_git|$action" >> "$TRASH_BUCKET_ROWS_FILE"
  done < <(find "$trash_root" -maxdepth 1 -mindepth 1 -type d 2>/dev/null | sort)
}

collect_cleanup_plan() {
  : > "$CLEANUP_PLAN_ROWS_FILE"
  cleanup_plan_move_to_trash_files=0
  cleanup_plan_move_to_purge_files=0
  cleanup_plan_os_trash_candidate_files=0
  cleanup_plan_report_only_files=0
  cleanup_plan_execution_allowed_count=0
  cleanup_plan_row_count=0
  local_purge_os_trash_candidate_files=0

  local lw_root="$ROOT/local-workspace"
  local trash_root="$lw_root/local-trash-delete"
  local purge_root="$trash_root/local-purge"
  local today
  today="$(date -u +%Y-%m-%d)"

  if [[ -d "$lw_root" ]]; then
    local child
    while IFS= read -r child; do
      [[ -z "$child" ]] && continue
      local child_name="${child##*/}"
      local rel_path="local-workspace/$child_name"
      local files dirs reason policy_rule dest
      if ! path_list_contains "$contract_allowed_direct_children" "$child_name"; then
        files="$(count_files "$child")"
        dirs="$(count_dirs "$child")"
        reason="direct local-workspace child is not allowed by selected skeleton profile"
        policy_rule="local-workspace-skeleton-contract"
        dest="local-workspace/local-trash-delete/local-workspace-policy-$today/$child_name"
        append_cleanup_plan_row "lw-unexpected-$child_name" "local_workspace" "soft_move_to_trash" "$rel_path" "$dest" "$reason" "$policy_rule" "$files" "$dirs" "true" "T1" "none"
      elif [[ "$child_name" != local-* ]]; then
        files="$(count_files "$child")"
        dirs="$(count_dirs "$child")"
        reason="direct local-workspace child does not use required local- prefix"
        policy_rule="local-workspace-skeleton-contract"
        dest="local-workspace/local-trash-delete/local-workspace-policy-$today/$child_name"
        append_cleanup_plan_row "lw-prefix-$child_name" "local_workspace" "soft_move_to_trash" "$rel_path" "$dest" "$reason" "$policy_rule" "$files" "$dirs" "true" "T1" "none"
      fi
    done < <(find "$lw_root" -maxdepth 1 -mindepth 1 -type d 2>/dev/null | sort)
  fi

  local legacy_dir
  while IFS= read -r legacy_dir; do
    [[ -z "$legacy_dir" ]] && continue
    local rel_path="${legacy_dir#"$ROOT/"}"
    local legacy_name="${legacy_dir##*/}"
    local files dirs dest
    files="$(count_files "$legacy_dir")"
    dirs="$(count_dirs "$legacy_dir")"
    dest="local-workspace/local-trash-delete/legacy-local-workspace-bucket-$today/$legacy_name"
    append_cleanup_plan_row "lw-legacy-$legacy_name" "local_workspace" "soft_move_to_trash" "$rel_path" "$dest" "legacy bucket name is prohibited in active local-workspace lanes" "workspace-organization-policy" "$files" "$dirs" "true" "T1" "none"
  done < <(
    {
      [[ -d "$lw_root/local-working-files" ]] && find "$lw_root/local-working-files" -type d \( -name 'incoming-clutter' -o -name 'working-files' -o -name 'trash-delete' -o -name 'handoffs' -o -name 'reference-candidates' \) 2>/dev/null
      [[ -d "$lw_root/local-shared-dropoff" ]] && find "$lw_root/local-shared-dropoff" -type d \( -name 'incoming-clutter' -o -name 'working-files' -o -name 'trash-delete' -o -name 'handoffs' -o -name 'reference-candidates' \) 2>/dev/null
    } | sort
  )

  while IFS='|' read -r rel_path file_count dir_count stale_files has_git action; do
    [[ -z "$rel_path" ]] && continue
    [[ "$action" == "review_for_local_purge" ]] || continue
    local name="${rel_path##*/}"
    append_cleanup_plan_row "trash-bucket-$name" "local_workspace" "move_to_local_purge" "$rel_path" "local-workspace/local-trash-delete/local-purge/$name" "root local-trash-delete bucket is stale, high-volume, or repo-shaped" "local-trash-delete-retention" "$file_count" "$dir_count" "true" "T1" "none"
  done < "$TRASH_BUCKET_ROWS_FILE"

  if [[ -d "$purge_root" ]]; then
    local purge_files
    purge_files="$(find "$purge_root" -type f -mtime +"$LOCAL_PURGE_OS_TRASH_DAYS" 2>/dev/null | wc -l | tr -d ' ')"
    local_purge_os_trash_candidate_files="$purge_files"
    if [[ "$purge_files" -gt 0 ]]; then
      local os_allowed="false"
      [[ "$LOCAL_PURGE_OS_TRASH_ALLOWED" == "1" ]] && os_allowed="true"
      append_cleanup_plan_row "purge-os-trash-candidates" "local_workspace" "os_trash_candidate" "local-workspace/local-trash-delete/local-purge" "~/.Trash" "local-purge files exceed OS Trash threshold" "local-trash-delete-retention" "$purge_files" "1" "$os_allowed" "T1" "os_trash"
    fi
  fi

  while IFS='|' read -r name local_matches canon_matches; do
    [[ -z "$name" ]] && continue
    append_cleanup_plan_row "duplicate-name-$name" "local_workspace" "report_only" "local-workspace/local-working-files/**/$name" "" "local working filename duplicates a repo filename; human review required" "duplicate-name-guardrail" "$local_matches" "0" "false" "T1" "none"
  done < "$DUPLICATE_ROWS_FILE"
}

collect_repo_temporal_candidates() {
  local tier="$1"
  : > "$REPO_TEMPORAL_ROWS_FILE"
  repo_temporal_candidate_count=0
  repo_temporal_candidate_files=0

  [[ "$tier" == "T2" || "$tier" == "T3" ]] || return 0

  while IFS='|' read -r repo rel_path pulse_enabled cleanup_enabled thread_visible verified notes; do
    [[ -z "${repo// }" ]] && continue
    [[ "$repo" =~ ^# ]] && continue
    [[ "${cleanup_enabled:-0}" == "1" ]] || continue
    [[ "${verified:-0}" == "1" ]] || continue

    local abs_path="$ROOT/$rel_path"
    [[ -d "$abs_path" ]] || continue

    local metadata_path
    while IFS= read -r metadata_path; do
      [[ -z "$metadata_path" ]] && continue
      if grep -Eq 'is_temporal[[:space:]]*[:=][[:space:]]*true' "$metadata_path" 2>/dev/null &&
         grep -Eq 'cleanup_status[[:space:]]*[:=][[:space:]]*"?((ready)|(purge)|(delete)|(deleted))"?' "$metadata_path" 2>/dev/null; then
        local rel_metadata="${metadata_path#"$ROOT/"}"
        repo_temporal_candidate_count=$((repo_temporal_candidate_count + 1))
        repo_temporal_candidate_files=$((repo_temporal_candidate_files + 1))
        echo "$repo|$rel_metadata|$tier|report_only|is_temporal=true with cleanup_status ready/purge/delete requires repo-aware review" >> "$REPO_TEMPORAL_ROWS_FILE"
      fi
    done < <(find "$abs_path" \( -path '*/.git' -o -path '*/.git/*' -o -path '*/node_modules' -o -path '*/node_modules/*' \) -prune -o -type f \( -name '*.json' -o -name '*.toml' -o -name '*.yaml' -o -name '*.yml' -o -name '*.md' \) -print 2>/dev/null)
  done < "$REGISTRY_FILE"
}

collect_branch_residue() {
  stale_local_branch_count=0
  stale_remote_branch_count=0
  open_pr_count=0
  stale_branch_rows=""
  open_pr_rows=""
  : > "$STALE_BRANCH_ROWS_FILE"
  : > "$OPEN_PR_ROWS_FILE"

  while IFS='|' read -r repo rel_path pulse_enabled cleanup_enabled thread_visible verified notes; do
    [[ -z "${repo// }" ]] && continue
    [[ "$repo" =~ ^# ]] && continue
    [[ "${cleanup_enabled:-0}" == "1" ]] || continue
    [[ "${verified:-0}" == "1" ]] || continue

    local abs_path="$ROOT/$rel_path"
    [[ -d "$abs_path/.git" ]] || continue

    while IFS= read -r branch; do
      [[ -z "$branch" ]] && continue
      stale_local_branch_count=$((stale_local_branch_count + 1))
      echo "$repo|local|$branch" >> "$STALE_BRANCH_ROWS_FILE"
    done < <(git -C "$abs_path" for-each-ref refs/heads --format='%(refname:short)' | grep -E '^codex/' || true)

    while IFS= read -r branch; do
      [[ -z "$branch" ]] && continue
      stale_remote_branch_count=$((stale_remote_branch_count + 1))
      echo "$repo|remote|$branch" >> "$STALE_BRANCH_ROWS_FILE"
    done < <(git -C "$abs_path" for-each-ref refs/remotes/origin/codex --format='%(refname:short)' || true)

    if command -v gh >/dev/null 2>&1; then
      local pr_json=""
      if pr_json="$(run_with_timeout "$NETWORK_TIMEOUT_SECONDS" gh pr list -R "BitPod-App/$repo" --state open --limit 100 --json number,headRefName,url 2>/dev/null)"; then
        :
      else
        pr_status=$?
        if [[ "$pr_status" -eq 124 ]]; then
          append_network_probe_failure "repo_audit" "$repo" "gh_pr_list" "timed out after ${NETWORK_TIMEOUT_SECONDS}s"
        fi
        pr_json=""
      fi
      if [[ -n "$pr_json" && "$pr_json" != "[]" ]]; then
        while IFS= read -r row; do
          [[ -z "$row" ]] && continue
          open_pr_count=$((open_pr_count + 1))
          echo "$repo|$row" >> "$OPEN_PR_ROWS_FILE"
        done < <(printf '%s' "$pr_json" | python3 -c 'import json,sys
try:
    data=json.load(sys.stdin)
except Exception:
    data=[]
for item in data:
    print("{}|{}|{}".format(item.get("number"), item.get("headRefName"), item.get("url")))')
      fi
    fi
  done < "$REGISTRY_FILE"

  [[ -f "$STALE_BRANCH_ROWS_FILE" ]] && stale_branch_rows="$(cat "$STALE_BRANCH_ROWS_FILE")"
  [[ -f "$OPEN_PR_ROWS_FILE" ]] && open_pr_rows="$(cat "$OPEN_PR_ROWS_FILE")"
}

collect_medium_checks() {
  : > "$TMP_IN_SHA"
  : > "$TMP_CANON_SHA"

  if [[ -d "$ROOT/local-workspace/local-working-files" ]]; then
    find "$ROOT/local-workspace/local-working-files" -type f -name '*.md' -print0 2>/dev/null | \
      xargs -0 shasum -a 256 | sort > "$TMP_IN_SHA" || true
  fi

  local canon_md_dirs=()
  while IFS='|' read -r repo rel_path pulse_enabled cleanup_enabled thread_visible verified notes; do
    [[ -z "${repo// }" ]] && continue
    [[ "$repo" =~ ^# ]] && continue
    [[ "${cleanup_enabled:-0}" == "1" ]] || continue
    [[ "${verified:-0}" == "1" ]] || continue
    [[ -d "$ROOT/$rel_path" ]] && canon_md_dirs+=("$ROOT/$rel_path")
  done < "$REGISTRY_FILE"

  if [[ "${#canon_md_dirs[@]}" -gt 0 ]]; then
    find "${canon_md_dirs[@]}" -type f -name '*.md' -print0 2>/dev/null | \
      xargs -0 shasum -a 256 | sort > "$TMP_CANON_SHA" || true
  fi

  scanned_reference_md=0
  exact_duplicate_md=0
  [[ -f "$TMP_IN_SHA" ]] && scanned_reference_md="$(wc -l < "$TMP_IN_SHA" | tr -d ' ')"
  if [[ "$scanned_reference_md" -gt 0 && -s "$TMP_CANON_SHA" ]]; then
    exact_duplicate_md="$(join -j 1 "$TMP_IN_SHA" "$TMP_CANON_SHA" | wc -l | tr -d ' ')"
  fi
}

collect_zone_rows() {
  : > "$ZONE_ROWS_FILE"
  strict_canonical_zone_issues=0
  report_only_zone_count=0
  strict_zone_count=0

  if [[ ! -f "$ZONE_POLICY_FILE" ]]; then
    echo "ZONE_POLICY|MISSING|$ZONE_POLICY_FILE|0|0|0|missing zone policy" >> "$ZONE_ROWS_FILE"
    strict_canonical_zone_issues=1
    return 0
  fi

  while IFS='|' read -r zone mode rel_path notes; do
    [[ -z "${zone// }" ]] && continue
    [[ "$zone" =~ ^# ]] && continue

    local abs_path="$ROOT/$rel_path"
    local status="OK"
    local file_count=0
    local dup_names=0
    local large_files=0

    if [[ "$mode" == "REPORT_ONLY" ]]; then
      report_only_zone_count=$((report_only_zone_count + 1))
    elif [[ "$mode" == "STRICT_CANONICAL" ]]; then
      strict_zone_count=$((strict_zone_count + 1))
    fi

    if [[ ! -d "$abs_path" ]]; then
      status="MISSING"
      if [[ "$mode" == "STRICT_CANONICAL" ]]; then
        strict_canonical_zone_issues=$((strict_canonical_zone_issues + 1))
      fi
    else
      file_count="$(find "$abs_path" -type f 2>/dev/null | wc -l | tr -d ' ')"
      dup_names="$(find "$abs_path" -type f -exec basename {} \; 2>/dev/null | sort | uniq -d | wc -l | tr -d ' ')"
      large_files="$(find "$abs_path" -type f -size +10M 2>/dev/null | wc -l | tr -d ' ')"
    fi

    echo "$zone|$mode|$rel_path|$status|$file_count|$dup_names|$large_files|${notes:-none}" >> "$ZONE_ROWS_FILE"
  done < "$ZONE_POLICY_FILE"
}

collect_full_checks() {
  dir_count_depth2="$(find "$ROOT" -maxdepth 2 -type d 2>/dev/null | wc -l | tr -d ' ')"
  file_count_depth2="$(find "$ROOT" -maxdepth 2 -type f 2>/dev/null | wc -l | tr -d ' ')"
  collect_zone_rows
}

quick_gate_status() {
  if [[ "$active_legacy_bucket_hits" -eq 0 &&
        "$unexpected_local_workspace_children" -eq 0 &&
        "$non_local_prefix_direct_children" -eq 0 &&
        "$trash_actionable_bucket_count" -eq 0 ]]; then
    echo "STOP_OK"
  else
    echo "ESCALATE_RECOMMENDED"
  fi
}

medium_gate_status() {
  if [[ "$(quick_gate_status)" == "STOP_OK" &&
        "$exact_duplicate_md" -eq 0 &&
        "$likely_duplicate_filename_count" -eq 0 ]]; then
    echo "STOP_OK"
  else
    echo "ESCALATE_RECOMMENDED"
  fi
}

t3_local_workspace_pass() {
  if [[ "$active_legacy_bucket_hits" -eq 0 &&
        "$unexpected_local_workspace_children" -eq 0 &&
        "$non_local_prefix_direct_children" -eq 0 &&
        "$trash_actionable_bucket_count" -eq 0 &&
        "$likely_duplicate_filename_count" -eq 0 &&
        "$exact_duplicate_md" -eq 0 &&
        "$strict_canonical_zone_issues" -eq 0 ]]; then
    echo "PASS"
  else
    echo "FAIL"
  fi
}

cleanup_overall_result() {
  local tier="$1"
  local include_local_workspace="$2"

  if [[ "$tier" != "T3" ]]; then
    echo "NOT VERIFIED"
    return 0
  fi

  local local_pass="PASS"
  [[ "$include_local_workspace" -eq 1 ]] && local_pass="$(t3_local_workspace_pass)"
  if [[ "$repo_total" -gt 0 &&
        "$code1" -eq "$repo_total" &&
        "$code2" -eq 0 &&
        "$local_pass" == "PASS" &&
        "$registry_problem_count" -eq 0 &&
        "$network_probe_fail_count" -eq 0 &&
        "$stale_local_branch_count" -eq 0 &&
        "$stale_remote_branch_count" -eq 0 &&
        "$open_pr_count" -eq 0 ]]; then
    echo "PORCELAIN"
  else
    echo "FRACTURED"
  fi
}

cleanup_overall_verification() {
  local tier="$1"
  if [[ "$tier" == "T3" ]]; then
    if [[ "$code2" -eq 0 &&
          "$registry_problem_count" -eq 0 &&
          "$network_probe_fail_count" -eq 0 &&
          "$stale_local_branch_count" -eq 0 &&
          "$stale_remote_branch_count" -eq 0 &&
          "$open_pr_count" -eq 0 ]]; then
      echo "VERIFIED"
    else
      echo "NOT VERIFIED"
    fi
  else
    echo "NOT VERIFIED"
  fi
}

cleanup_verification_detail() {
  local tier="$1"
  if [[ "$tier" == "T3" ]]; then
    if [[ "$code2" -gt 0 ]]; then
      echo "Fresh all-repo parity was attempted, but one or more repos could not be verified cleanly."
    elif [[ "$registry_problem_count" -gt 0 ]]; then
      echo "Repo registry problems prevented a fully verified cleanup pass."
    elif [[ "$network_probe_fail_count" -gt 0 ]]; then
      echo "One or more bounded network probes timed out, so cleanup truth could not be fully verified."
    elif [[ "$stale_local_branch_count" -gt 0 || "$stale_remote_branch_count" -gt 0 || "$open_pr_count" -gt 0 ]]; then
      echo "Stale codex branches or open pull requests prevented a fully verified cleanup pass."
    else
      echo "Fresh all-repo parity verification completed in this run."
    fi
  elif [[ "$tier" == "T1" ]]; then
    echo "T1 is local-workspace only; repo parity is intentionally not scanned."
  else
    echo "Repo parity in $tier is advisory only. Use T3 for authoritative fresh all-repo verification."
  fi
}

reset_repo_summary() {
  repo_rows=""
  repo_total=0
  code1=0
  code2=0
  code3=0
  code4=0
  code5=0
  pulse_matched=0
  pulse_local_diverged=0
  pulse_remote_mismatch=0
  pulse_unlinked=0
  cleanup_likely_match=0
  cleanup_local_diverged=0
  cleanup_remote_mismatch=0
  cleanup_unlinked=0
  repo_fetch_failed=0
  repo_verified_count=0
  repo_not_verified_count=0
  registry_problem_count=0
  registry_problem_lines=""
  network_probe_fail_count=0
  network_probe_rows=""
}

reset_workspace_metrics() {
  working_files=0
  trash_files=0
  handoff_files=0
  pm_only_files=0
  codex_state_files=0
  shared_dropoff_files=0
  trash_soft_purge_pending_files=0
  trash_root_bucket_count=0
  trash_actionable_bucket_count=0
  cleanup_plan_move_to_trash_files=0
  cleanup_plan_move_to_purge_files=0
  cleanup_plan_os_trash_candidate_files=0
  cleanup_plan_report_only_files=0
  cleanup_plan_execution_allowed_count=0
  cleanup_plan_row_count=0
  local_purge_os_trash_candidate_files=0
  repo_temporal_candidate_count=0
  repo_temporal_candidate_files=0
  likely_duplicate_filename_count=0
  active_legacy_bucket_hits=0
  unexpected_local_workspace_children=0
  non_local_prefix_direct_children=0
  scanned_reference_md=0
  exact_duplicate_md=0
  dir_count_depth2=0
  file_count_depth2=0
  strict_canonical_zone_issues=0
  report_only_zone_count=0
  strict_zone_count=0
  stale_local_branch_count=0
  stale_remote_branch_count=0
  open_pr_count=0
  network_probe_fail_count=0
  network_probe_rows=""
  stale_branch_rows=""
  open_pr_rows=""
  : > "$ZONE_ROWS_FILE"
  : > "$TRASH_BUCKET_ROWS_FILE"
  : > "$CLEANUP_PLAN_ROWS_FILE"
  : > "$DUPLICATE_ROWS_FILE"
  : > "$REPO_TEMPORAL_ROWS_FILE"
}

emit_registry_problems() {
  if [[ "$registry_problem_count" -eq 0 ]]; then
    echo "- registry_problems=0"
    return 0
  fi

  echo "- registry_problems=$registry_problem_count"
  while IFS='|' read -r repo problem detail; do
    [[ -z "$repo" ]] && continue
    echo "- registry_problem=$repo problem=$problem detail=$detail"
  done <<< "$registry_problem_lines"
}

emit_parity_summary_section() {
  local surface="$1"
  local tier="$2"
  local overall_label="$3"
  local overall_verification="$4"
  local require_fresh="$5"

  print_section "Parity summary"
  if [[ "$surface" == "cleanup" && "$tier" == "T1" ]]; then
    echo "- repo_scope=skipped"
    echo "- detail=T1 is local-workspace only; use T2 for inferred repo clutter or T3 for authoritative repo verification."
    return 0
  fi
  echo "- repos_scanned=$repo_total"
  echo "- verification=$overall_verification"
  echo "- codes: 1:1=$code1 1:2=$code2 1:3=$code3 1:4=$code4 1:5=$code5"

  if [[ "$surface" == "pulse" ]]; then
    echo "- states: matched=$pulse_matched local_diverged=$pulse_local_diverged remote_mismatch=$pulse_remote_mismatch unlinked=$pulse_unlinked"
    echo "- overall=$overall_label"
  else
    echo "- states: likely_match=$cleanup_likely_match local_diverged=$cleanup_local_diverged remote_mismatch=$cleanup_remote_mismatch unlinked=$cleanup_unlinked"
    echo "- overall=$overall_label"
    if [[ "$tier" == "T3" ]]; then
      echo "- parity_mode=authoritative"
    else
      echo "- parity_mode=advisory"
    fi
  fi

  echo "- fresh_verification_requested=$(render_bool "$require_fresh")"
}

pulse_overall_result() {
  if [[ "$repo_total" -gt 0 && "$code1" -eq "$repo_total" && "$code2" -eq 0 && "$registry_problem_count" -eq 0 && "${1:-}" == "VERIFIED" ]]; then
    echo "PORCELAIN"
  else
    echo "REPORT ONLY"
  fi
}

emit_repo_detail_row() {
  local surface="$1"
  local tier="$2"
  local row="$3"

  IFS='|' read -r name code status_key verification verification_detail meaning branch upstream remote_fresh dirty ahead behind head_eq_upstream <<< "$row"
  local label
  if [[ "$surface" == "pulse" ]]; then
    label="$(pulse_label_for_code "$code")"
  else
    label="$(cleanup_label_for_code "$code")"
  fi

  echo "- 1:$code | $name@$branch vs $upstream | $label | verification=$verification | detail=$verification_detail | note=$meaning | EVIDENCE(fetch_fresh=$remote_fresh,dirty_items=$dirty,ahead=$ahead,behind=$behind,head_eq_upstream=$head_eq_upstream)"
}

emit_cleanup_repo_details() {
  local tier="$1"
  local result="$2"

  if [[ "$tier" == "T1" ]]; then
    echo "- repo_findings=skipped_for_t1"
    return 0
  fi

  if [[ "$result" == "PORCELAIN" ]]; then
    echo "- repo_findings=none"
    return 0
  fi

  while IFS= read -r row; do
    [[ -z "$row" ]] && continue
    IFS='|' read -r name code status_key verification verification_detail meaning branch upstream remote_fresh dirty ahead behind head_eq_upstream <<< "$row"
    if [[ "$tier" == "T3" && "$code" -eq 1 ]]; then
      continue
    fi
    emit_repo_detail_row "cleanup" "$tier" "$row"
  done <<< "$repo_rows"
}

emit_pulse_repo_details() {
  if [[ "$code1" -eq "$repo_total" && "$repo_total" -gt 0 && "$code2" -eq 0 ]]; then
    echo "- repo_findings=none"
    return 0
  fi

  while IFS= read -r row; do
    [[ -z "$row" ]] && continue
    IFS='|' read -r name code status_key verification verification_detail meaning branch upstream remote_fresh dirty ahead behind head_eq_upstream <<< "$row"
    if [[ "$code" -eq 1 ]]; then
      continue
    fi
    emit_repo_detail_row "pulse" "T1" "$row"
  done <<< "$repo_rows"
}

emit_workspace_hygiene_section() {
  local include_local_workspace="$1"
  if [[ "$include_local_workspace" -eq 0 ]]; then
    print_section "Workspace hygiene"
    echo "- skipped=YES"
    echo "- detail=Local workspace checks were suppressed for this run."
    return 0
  fi

  print_section "Workspace hygiene"
  echo "- likely_duplicate_filename_count=$likely_duplicate_filename_count"
  echo "- active_legacy_bucket_hits=$active_legacy_bucket_hits"
  echo "- unexpected_local_workspace_children=$unexpected_local_workspace_children"
  echo "- non_local_prefix_direct_children=$non_local_prefix_direct_children"
  echo "- trash_soft_purge_pending_files=$trash_soft_purge_pending_files"
  echo "- trash_soft_purge_threshold_days=$trash_soft_purge_threshold_days"
  echo "- trash_root_buckets=$trash_root_bucket_count"
  echo "- trash_actionable_buckets=$trash_actionable_bucket_count"
  echo "- trash_action_threshold_files=$TRASH_BUCKET_ACTION_FILE_THRESHOLD"
  while IFS='|' read -r rel_path file_count dir_count stale_files has_git action; do
    [[ -z "$rel_path" ]] && continue
    [[ "$action" == "review_for_local_purge" ]] || continue
    echo "- trash_bucket=$rel_path action=$action files=$file_count dirs=$dir_count stale_files=$stale_files has_git=$has_git"
  done < "$TRASH_BUCKET_ROWS_FILE"
}

emit_queue_health_section() {
  local include_local_workspace="$1"
  if [[ "$include_local_workspace" -eq 0 ]]; then
    print_section "Queue health"
    echo "- skipped=YES"
    echo "- detail=Local workspace checks were suppressed for this run."
    return 0
  fi

  print_section "Queue health"
  echo "- working_files=$working_files"
  echo "- trash_files=$trash_files"
  echo "- handoff_files=$handoff_files"
  echo "- pm_only_files=$pm_only_files"
  echo "- codex_state_files=$codex_state_files"
  echo "- shared_dropoff_files=$shared_dropoff_files"
}

emit_cleanup_plan_section() {
  local include_local_workspace="$1"
  print_section "Cleanup plan"
  if [[ "$include_local_workspace" -eq 0 ]]; then
    echo "- skipped=YES"
    echo "- detail=Local workspace cleanup plan was suppressed for this run."
    return 0
  fi

  echo "- findings=$cleanup_plan_row_count"
  echo "- execution_allowed_findings=$cleanup_plan_execution_allowed_count"
  echo "- files_to_move_to_local_trash=$cleanup_plan_move_to_trash_files"
  echo "- files_to_move_to_local_purge=$cleanup_plan_move_to_purge_files"
  echo "- files_to_offer_for_os_trash=$cleanup_plan_os_trash_candidate_files"
  echo "- report_only_files=$cleanup_plan_report_only_files"
  echo "- local_trash_purge_threshold_days=$LOCAL_TRASH_PURGE_DAYS"
  echo "- local_purge_os_trash_threshold_days=$LOCAL_PURGE_OS_TRASH_DAYS"
  echo "- os_trash_permission_enabled=$( [[ "$LOCAL_PURGE_OS_TRASH_ALLOWED" == "1" ]] && echo YES || echo NO )"
  while IFS='|' read -r finding_id scope action path destination reason policy_rule file_count dir_count execution_allowed requires_tier requires_permission; do
    [[ -z "$finding_id" ]] && continue
    echo "- finding_id=$finding_id scope=$scope action=$action path=$path destination=${destination:-none} reason=\"$reason\" policy_rule=$policy_rule files=$file_count dirs=$dir_count execution_allowed=$execution_allowed requires_tier=$requires_tier requires_permission=$requires_permission"
  done < "$CLEANUP_PLAN_ROWS_FILE"
}

emit_tier_specific_section() {
  local tier="$1"
  local include_local_workspace="$2"

  print_section "Tier-specific checks"
  emit_registry_problems
  echo "- network_probe_failures=$network_probe_fail_count"
  while IFS='|' read -r surface repo operation detail; do
    [[ -z "$surface" ]] && continue
    echo "- network_probe_failure=surface=$surface repo=$repo operation=$operation detail=$detail"
  done <<< "$network_probe_rows"
  echo "- stale_local_codex_branches=$stale_local_branch_count"
  echo "- stale_remote_codex_branches=$stale_remote_branch_count"
  echo "- open_pull_requests=$open_pr_count"
  echo "- repo_temporal_candidates=$repo_temporal_candidate_count"
  echo "- repo_temporal_candidate_files=$repo_temporal_candidate_files"
  while IFS='|' read -r repo metadata tier_seen action reason; do
    [[ -z "$repo" ]] && continue
    if [[ "$tier" == "T2" ]]; then
      echo "- repo_temporal_candidate=$repo path=$metadata confidence=inferred action=$action reason=\"$reason\" next=run_T3_for_repo_truth"
    else
      echo "- repo_temporal_candidate=$repo path=$metadata confidence=verified action=$action reason=\"$reason\""
    fi
  done < "$REPO_TEMPORAL_ROWS_FILE"
  while IFS='|' read -r repo scope ref; do
    [[ -z "$repo" ]] && continue
    echo "- stale_ref=$repo scope=$scope ref=$ref"
  done <<< "$stale_branch_rows"
  while IFS='|' read -r repo number head_ref url; do
    [[ -z "$repo" ]] && continue
    echo "- open_pr=$repo number=$number head=$head_ref url=$url"
  done <<< "$open_pr_rows"

  if [[ "$include_local_workspace" -eq 0 ]]; then
    echo "- local_workspace_checks=SKIPPED"
    return 0
  fi

  echo "- quick_gate=$(quick_gate_status)"
  if [[ "$tier" == "T2" || "$tier" == "T3" ]]; then
    echo "- scanned_reference_md=$scanned_reference_md"
    echo "- exact_duplicate_md=$exact_duplicate_md"
    echo "- medium_gate=$(medium_gate_status)"
  fi
  if [[ "$tier" == "T3" ]]; then
    echo "- dir_count_depth2=$dir_count_depth2"
    echo "- file_count_depth2=$file_count_depth2"
    echo "- strict_canonical_zone_issues=$strict_canonical_zone_issues"
    echo "- strict_zone_count=$strict_zone_count"
    echo "- report_only_zone_count=$report_only_zone_count"
    echo "- local_workspace_status=$(t3_local_workspace_pass)"
    while IFS='|' read -r zone mode rel_path status file_count dup_names large_files notes; do
      [[ -z "$zone" ]] && continue
      echo "- zone=$zone mode=$mode path=$rel_path status=$status files=$file_count dup_names=$dup_names large_files_gt10mb=$large_files notes=$notes"
    done < "$ZONE_ROWS_FILE"
  fi
}

emit_cleanup_next_action() {
  local tier="$1"
  local result="$2"
  local include_local_workspace="$3"

  print_section "Next action"
  if [[ "$tier" == "T1" ]]; then
    if [[ "$include_local_workspace" -eq 1 && "$cleanup_plan_execution_allowed_count" -gt 0 ]]; then
      echo "- Would you like to execute safe local-workspace cleanup now? Scope would be local-workspace only and based on the Cleanup plan section above."
      echo "- To execute: run T1 cleanup execute local-workspace"
    fi
    echo "- Run T2 cleanup when you also want inferred repo clutter signals."
    echo "- Run T3 cleanup only when you need authoritative repo truth."
    if [[ "$include_local_workspace" -eq 1 ]]; then
      echo "- Use 'only repos' or 'no local workspace' if you want to suppress local-workspace checks for the next manual run."
    fi
    return 0
  fi

  if [[ "$tier" == "T2" ]]; then
    if [[ "$include_local_workspace" -eq 1 && "$cleanup_plan_execution_allowed_count" -gt 0 ]]; then
      echo "- Would you like to execute safe local-workspace cleanup now? Scope would be local-workspace only; repo parity would remain report-only."
      echo "- To execute: run T2 cleanup execute local-workspace"
    fi
    if [[ "$repo_temporal_candidate_count" -gt 0 ]]; then
      echo "- Repo temporal cleanup candidates were inferred; run T3 cleanup before treating repo cleanup as verified."
    fi
    echo "- Run T3 cleanup only when you need authoritative repo parity."
    if [[ "$include_local_workspace" -eq 1 ]]; then
      echo "- Use 'only repos' or 'no local workspace' if you want to suppress local-workspace checks for the next manual run."
    fi
    return 0
  fi

  if [[ "$result" == "PORCELAIN" ]]; then
    echo "- No cleanup action required."
  else
    if [[ "$include_local_workspace" -eq 1 && "$cleanup_plan_execution_allowed_count" -gt 0 ]]; then
      echo "- Would you like to execute safe local-workspace cleanup now? Scope would be local-workspace only; repo parity would remain report-only."
      echo "- To execute: run T3 cleanup execute local-workspace"
    fi
    echo "- Cleanup remains fractured; review the failing repo or workspace findings above and remediate until T3 passes."
  fi
}

emit_cleanup_report() {
  local tier="$1"
  local include_local_workspace="$2"
  local require_fresh="$3"

  local result overall_verification verification_detail
  result="$(cleanup_overall_result "$tier" "$include_local_workspace")"
  overall_verification="$(cleanup_overall_verification "$tier")"
  verification_detail="$(cleanup_verification_detail "$tier")"

  print_header "$tier Cleanup"
  print_section "Result"
  echo "- tier=$tier"
  echo "- scope=cleanup-audit"
  echo "- result=$result"
  if [[ "$tier" == "T1" ]]; then
    echo "- note=T1 is local-workspace only and can propose safe local-workspace cleanup."
  elif [[ "$tier" == "T2" ]]; then
    echo "- note=Repo parity in $tier is advisory only."
  else
    echo "- note=$( [[ "$result" == "PORCELAIN" ]] && echo "Full cleanup pass achieved." || echo "Full cleanup pass not achieved." )"
  fi

  print_section "Verification"
  echo "- overall=$overall_verification"
  echo "- detail=$verification_detail"

  emit_parity_summary_section "cleanup" "$tier" "$result" "$overall_verification" "$require_fresh"
  emit_cleanup_repo_details "$tier" "$result"
  emit_workspace_hygiene_section "$include_local_workspace"
  emit_queue_health_section "$include_local_workspace"
  emit_cleanup_plan_section "$include_local_workspace"
  emit_tier_specific_section "$tier" "$include_local_workspace"
  emit_cleanup_next_action "$tier" "$result" "$include_local_workspace"
}

unique_destination_path() {
  local destination="$1"
  if [[ ! -e "$destination" ]]; then
    printf '%s\n' "$destination"
    return 0
  fi

  local base="$destination"
  local suffix=1
  while [[ -e "${base}-$suffix" ]]; do
    suffix=$((suffix + 1))
  done
  printf '%s\n' "${base}-$suffix"
}

apply_safe_local_workspace_cleanup() {
  if [[ "$cleanup_plan_row_count" -eq 0 ]]; then
    return 0
  fi

  while IFS='|' read -r finding_id scope action path destination reason policy_rule file_count dir_count execution_allowed requires_tier requires_permission; do
    [[ -z "$finding_id" ]] && continue
    [[ "$scope" == "local_workspace" ]] || continue
    [[ "$execution_allowed" == "true" ]] || continue

    local src="$ROOT/$path"
    local dest="$ROOT/$destination"
    case "$action" in
      soft_move_to_trash|move_to_local_purge)
        [[ -e "$src" ]] || continue
        mkdir -p "$(dirname "$dest")"
        dest="$(unique_destination_path "$dest")"
        mv "$src" "$dest"
        ;;
      os_trash_candidate)
        [[ "$LOCAL_PURGE_OS_TRASH_ALLOWED" == "1" ]] || continue
        [[ -d "$src" ]] || continue
        mkdir -p "$HOME/.Trash"
        local item
        while IFS= read -r item; do
          [[ -z "$item" ]] && continue
          local trash_dest="$HOME/.Trash/${item##*/}"
          trash_dest="$(unique_destination_path "$trash_dest")"
          mv "$item" "$trash_dest"
        done < <(find "$src" -type f -mtime +"$LOCAL_PURGE_OS_TRASH_DAYS" 2>/dev/null | sort)
        ;;
    esac
  done < "$CLEANUP_PLAN_ROWS_FILE"
}

emit_pulse_report() {
  local require_fresh="$1"
  local event_name="$2"
  local overall_verification="VERIFIED"
  local verification_detail="Fresh parity verification completed for all scanned repos."
  local pulse_result

  if [[ "$code2" -gt 0 || "$registry_problem_count" -gt 0 ]]; then
    overall_verification="NOT VERIFIED"
    if [[ "$repo_fetch_failed" -gt 0 ]]; then
      verification_detail="One or more repos could not be fresh-verified; report-only parity is based partly on local state."
    else
      verification_detail="This pulse is report-only and includes local-only repo assessments."
    fi
  fi
  pulse_result="$(pulse_overall_result "$overall_verification")"

  echo "Parity Pulse"
  echo "Timestamp: $NOW"
  echo "- event=$event_name"
  echo "- scope=report-only"
  echo "- result=$pulse_result"
  echo "- verification=$overall_verification"
  echo "- detail=$verification_detail"
  emit_parity_summary_section "pulse" "T1" "$pulse_result" "$overall_verification" "$require_fresh"
  emit_pulse_repo_details
  if [[ "$registry_problem_count" -gt 0 ]]; then
    print_section "Registry"
    emit_registry_problems
  fi
}

prepare_workspace_metrics() {
  local include_local_workspace="$1"
  local tier="$2"
  if [[ "$tier" == "T3" ]]; then
    collect_branch_residue
  fi
  if [[ "$include_local_workspace" -eq 0 ]]; then
    return 0
  fi

  collect_queue_health
  collect_workspace_hygiene
  collect_cleanup_plan
  if [[ "$tier" == "T2" || "$tier" == "T3" ]]; then
    collect_medium_checks
  fi
  if [[ "$tier" == "T3" ]]; then
    collect_full_checks
  fi
}

run_cleanup_tier() {
  local tier="$1"
  local include_local_workspace="$2"
  local execute_local_workspace="${3:-0}"
  local require_fresh=0
  [[ "$tier" == "T3" ]] && require_fresh=1

  reset_repo_summary
  reset_workspace_metrics

  if [[ "$tier" != "T1" ]]; then
    assert_registry_ready
    build_repo_rows "cleanup" "$require_fresh"
    collect_registry_problems
    summarize_repo_rows
    collect_repo_temporal_candidates "$tier"
  fi
  prepare_workspace_metrics "$include_local_workspace" "$tier"
  if [[ "$execute_local_workspace" -eq 1 ]]; then
    apply_safe_local_workspace_cleanup
    collect_queue_health
    collect_workspace_hygiene
    collect_cleanup_plan
  fi
  emit_cleanup_report "$tier" "$include_local_workspace" "$require_fresh"

  if [[ "$tier" == "T1" ]]; then
    return 0
  fi
  if [[ "$tier" == "T2" ]]; then
    [[ "$(medium_gate_status)" == "STOP_OK" ]] && return 0 || return 20
  fi
  [[ "$(cleanup_overall_result "$tier" "$include_local_workspace")" == "PORCELAIN" ]] && return 0 || return 30
}

run_cleanup_auto() {
  local include_local_workspace="$1"
  local force_full="$2"

  local t1_status=0
  if run_cleanup_tier "T1" "$include_local_workspace" 0 >/dev/null 2>&1; then
    t1_status=0
  else
    t1_status=$?
  fi
  if [[ "$t1_status" -eq 0 && "$force_full" -eq 0 ]]; then
    run_cleanup_tier "T1" "$include_local_workspace" 0
    return 0
  fi

  local t2_status=0
  if run_cleanup_tier "T2" "$include_local_workspace" 0 >/dev/null 2>&1; then
    t2_status=0
  else
    t2_status=$?
  fi
  if [[ "$t2_status" -eq 0 && "$force_full" -eq 0 ]]; then
    run_cleanup_tier "T2" "$include_local_workspace" 0
    return 0
  fi

  run_cleanup_tier "T3" "$include_local_workspace" 0
}

run_parity_pulse() {
  local require_fresh="$1"
  local event_name="$2"

  reset_repo_summary

  assert_registry_ready
  build_repo_rows "pulse" "$require_fresh"
  collect_registry_problems
  summarize_repo_rows
  emit_pulse_report "$require_fresh" "$event_name"
}

main() {
  local raw="${*:-run audit}"
  local q
  q="$(printf '%s' "$raw" | normalize)"

  if has_phrase "$q" "__parity_pulse__" || has_phrase "$q" "parity-pulse" || has_phrase "$q" "parity pulse"; then
    local pulse_fresh=0
    local pulse_event="manual"
    if has_phrase "$q" "fresh" || has_phrase "$q" "pre-push" || has_phrase "$q" "post-push"; then
      pulse_fresh=1
    fi
    local maybe_event
    maybe_event="$(printf '%s\n' "$raw" | sed -n 's/.*event=\([^ ]*\).*/\1/p')"
    [[ -n "$maybe_event" ]] && pulse_event="$maybe_event"
    run_parity_pulse "$pulse_fresh" "$pulse_event"
    exit 0
  fi

  local include_local_workspace=1
  if has_phrase "$q" "no local workspace" || has_phrase "$q" "only repos" || has_phrase "$q" "repo only" || has_phrase "$q" "repos only"; then
    include_local_workspace=0
  fi

  local force_full=0
  local auto=0
  local execute_local_workspace=0
  has_phrase "$q" "force full" && force_full=1
  has_phrase "$q" " auto " && auto=1
  has_phrase "$q" "auto cleanup" && auto=1
  has_phrase "$q" "full audit auto" && auto=1
  if (has_phrase "$q" "execute" || has_phrase "$q" "apply") &&
     (has_phrase "$q" "local-workspace" || has_phrase "$q" "local workspace"); then
    execute_local_workspace=1
  fi

  local tier="T1"
  if has_phrase "$q" "t3" || has_phrase "$q" "tier 3" || has_phrase "$q" "v3" || has_phrase "$q" "full"; then
    tier="T3"
  elif has_phrase "$q" "t2" || has_phrase "$q" "tier 2" || has_phrase "$q" "v2" || has_phrase "$q" "medium"; then
    tier="T2"
  elif has_phrase "$q" "t1" || has_phrase "$q" "tier 1" || has_phrase "$q" "v1" || has_phrase "$q" "quick"; then
    tier="T1"
  fi

  if [[ "$auto" -eq 1 ]]; then
    run_cleanup_auto "$include_local_workspace" "$force_full"
    exit 0
  fi

  run_cleanup_tier "$tier" "$include_local_workspace" "$execute_local_workspace"
}

main "$@"
