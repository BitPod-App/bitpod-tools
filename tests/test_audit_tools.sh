#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
AUDIT_CTL="$PROJECT_ROOT/audit_ctl.sh"
REFRESH_REGISTRY="$PROJECT_ROOT/scripts/refresh_repo_registry.sh"
INSTALL_HOOKS="$PROJECT_ROOT/scripts/install_parity_pulse_hooks.sh"
SCHEDULED_CLEANUP="$PROJECT_ROOT/scripts/run_scheduled_cleanup_audit.sh"
PARITY_PULSE_EMIT="$PROJECT_ROOT/scripts/parity_pulse_emit.sh"

TEST_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/audit_tools_test.XXXXXX")"
trap 'rm -rf "$TEST_ROOT"' EXIT

WORKSPACE_ROOT="$TEST_ROOT/workspace"
REMOTE_ROOT="$TEST_ROOT/remotes"
CONFIG_ROOT="$WORKSPACE_ROOT/bitpod-tools/config"
REGISTRY_FILE="$CONFIG_ROOT/repo_registry.tsv"
PERFECT_REGISTRY_FILE="$CONFIG_ROOT/repo_registry_perfect.tsv"
HOOK_REGISTRY_FILE="$CONFIG_ROOT/repo_registry_hooks.tsv"
ZONE_POLICY_FILE="$CONFIG_ROOT/cleanup_zones_policy.tsv"
CONTRACT_FILE="$TEST_ROOT/local-workspace-skeleton-contract.toml"

fail() {
  echo "FAIL: $1" >&2
  exit 1
}

assert_contains() {
  local haystack="$1"
  local needle="$2"
  [[ "$haystack" == *"$needle"* ]] || fail "expected output to contain: $needle"
}

assert_not_contains() {
  local haystack="$1"
  local needle="$2"
  [[ "$haystack" != *"$needle"* ]] || fail "did not expect output to contain: $needle"
}

assert_file_exists() {
  local path="$1"
  [[ -f "$path" ]] || fail "expected file to exist: $path"
}

assert_file_missing() {
  local path="$1"
  [[ ! -e "$path" ]] || fail "expected path to be absent: $path"
}

assert_equals() {
  local expected="$1"
  local actual="$2"
  [[ "$expected" == "$actual" ]] || fail "expected '$expected' but got '$actual'"
}

DIRTY_BETA_STASHED=0
DELTA_OLD_SHA=""
GAMMA_REMOTE_ADDED=0

make_workspace_fully_clean() {
  DIRTY_BETA_STASHED=0
  DELTA_OLD_SHA="$(git -C "$WORKSPACE_ROOT/delta" rev-parse HEAD)"
  GAMMA_REMOTE_ADDED=0

  if [[ -n "$(git -C "$WORKSPACE_ROOT/beta" status --porcelain)" ]]; then
    git -C "$WORKSPACE_ROOT/beta" stash push -u -m audit-test-dirty >/dev/null
    DIRTY_BETA_STASHED=1
  fi

  git -C "$WORKSPACE_ROOT/delta" pull --ff-only >/dev/null

  if ! git -C "$WORKSPACE_ROOT/gamma" remote get-url origin >/dev/null 2>&1; then
    git init --bare "$REMOTE_ROOT/gamma.git" >/dev/null
    git -C "$WORKSPACE_ROOT/gamma" remote add origin "$REMOTE_ROOT/gamma.git"
    git -C "$WORKSPACE_ROOT/gamma" push -u origin main >/dev/null
    git -C "$REMOTE_ROOT/gamma.git" symbolic-ref HEAD refs/heads/main >/dev/null
    GAMMA_REMOTE_ADDED=1
  fi
}

restore_dirty_workspace_shape() {
  if [[ -n "$DELTA_OLD_SHA" ]]; then
    git -C "$WORKSPACE_ROOT/delta" reset --hard "$DELTA_OLD_SHA" >/dev/null
  fi

  if [[ "$GAMMA_REMOTE_ADDED" -eq 1 ]]; then
    git -C "$WORKSPACE_ROOT/gamma" remote remove origin >/dev/null
    rm -rf "$REMOTE_ROOT/gamma.git"
  fi

  if [[ "$DIRTY_BETA_STASHED" -eq 1 ]]; then
    git -C "$WORKSPACE_ROOT/beta" stash pop >/dev/null
  fi

  DIRTY_BETA_STASHED=0
  DELTA_OLD_SHA=""
  GAMMA_REMOTE_ADDED=0
}

git_commit_all() {
  local repo_path="$1"
  local message="$2"
  git -C "$repo_path" add -A >/dev/null
  git -C "$repo_path" -c user.name="Codex Test" -c user.email="codex@example.com" commit -m "$message" >/dev/null
}

create_tracked_repo() {
  local name="$1"
  local repo_path="$WORKSPACE_ROOT/$name"
  local remote_path="$REMOTE_ROOT/$name.git"

  git init -b main "$repo_path" >/dev/null
  echo "$name" > "$repo_path/README.md"
  git_commit_all "$repo_path" "initial"

  git init --bare "$remote_path" >/dev/null
  git -C "$repo_path" remote add origin "$remote_path"
  git -C "$repo_path" push -u origin main >/dev/null
  git -C "$remote_path" symbolic-ref HEAD refs/heads/main >/dev/null
}

create_linked_worktree_repo() {
  local name="$1"
  local source_path="$TEST_ROOT/${name}_source"
  local repo_path="$WORKSPACE_ROOT/$name"
  local remote_path="$REMOTE_ROOT/$name.git"
  local branch_name="${name}-worktree"

  git init -b main "$source_path" >/dev/null
  echo "$name" > "$source_path/README.md"
  git_commit_all "$source_path" "initial"

  git init --bare "$remote_path" >/dev/null
  git -C "$source_path" remote add origin "$remote_path"
  git -C "$source_path" push -u origin main >/dev/null
  git -C "$remote_path" symbolic-ref HEAD refs/heads/main >/dev/null

  git -C "$source_path" worktree add -b "$branch_name" "$repo_path" origin/main >/dev/null
  git -C "$repo_path" branch --set-upstream-to=origin/main "$branch_name" >/dev/null
}

advance_remote() {
  local name="$1"
  local clone_path="$TEST_ROOT/${name}_remote_clone"

  git clone "$REMOTE_ROOT/$name.git" "$clone_path" >/dev/null
  echo "remote update" >> "$clone_path/README.md"
  git_commit_all "$clone_path" "remote advance"
  git -C "$clone_path" push >/dev/null
  rm -rf "$clone_path"
}

run_audit_capture() {
  local registry_file="$1"
  local request="$2"
  BITPOD_APP_ROOT="$WORKSPACE_ROOT" \
  BITPOD_REPO_REGISTRY_FILE="$registry_file" \
  BITPOD_CLEANUP_ZONE_POLICY_FILE="$ZONE_POLICY_FILE" \
  BITPOD_LOCAL_WORKSPACE_CONTRACT_FILE="$CONTRACT_FILE" \
  "$AUDIT_CTL" "$request"
}

run_scheduled_capture() {
  local registry_file="$1"
  BITPOD_APP_ROOT="$WORKSPACE_ROOT" \
  BITPOD_REPO_REGISTRY_FILE="$registry_file" \
  BITPOD_CLEANUP_ZONE_POLICY_FILE="$ZONE_POLICY_FILE" \
  BITPOD_LOCAL_WORKSPACE_CONTRACT_FILE="$CONTRACT_FILE" \
  "$SCHEDULED_CLEANUP"
}

run_pulse_emit() {
  local registry_file="$1"
  local event_name="$2"
  local repo_path="$3"
  shift 3
  BITPOD_APP_ROOT="$WORKSPACE_ROOT" \
  BITPOD_REPO_REGISTRY_FILE="$registry_file" \
  BITPOD_CLEANUP_ZONE_POLICY_FILE="$ZONE_POLICY_FILE" \
  BITPOD_LOCAL_WORKSPACE_CONTRACT_FILE="$CONTRACT_FILE" \
  "$@" \
  "$PARITY_PULSE_EMIT" "$event_name" "$repo_path" 2>&1
}

run_audit_capture_with_path() {
  local registry_file="$1"
  local request="$2"
  local path_override="$3"
  BITPOD_APP_ROOT="$WORKSPACE_ROOT" \
  BITPOD_REPO_REGISTRY_FILE="$registry_file" \
  BITPOD_CLEANUP_ZONE_POLICY_FILE="$ZONE_POLICY_FILE" \
  BITPOD_LOCAL_WORKSPACE_CONTRACT_FILE="$CONTRACT_FILE" \
  BITPOD_AUDIT_NETWORK_TIMEOUT_SECONDS=1 \
  PATH="$path_override:$PATH" \
  "$AUDIT_CTL" "$request"
}

setup_workspace() {
  mkdir -p "$CONFIG_ROOT"
  mkdir -p "$(dirname "$CONTRACT_FILE")"
  mkdir -p "$WORKSPACE_ROOT/bitpod-tools/scripts"
  mkdir -p "$REMOTE_ROOT"
  mkdir -p "$WORKSPACE_ROOT/local-workspace/local-working-files/local-reference"
  mkdir -p "$WORKSPACE_ROOT/local-workspace/local-trash-delete"
  mkdir -p "$WORKSPACE_ROOT/local-workspace/local-trash-delete/local-purge"
  mkdir -p "$WORKSPACE_ROOT/local-workspace/local-personal-only"

  ln -s "$AUDIT_CTL" "$WORKSPACE_ROOT/bitpod-tools/audit_ctl.sh"
  ln -s "$PROJECT_ROOT/scripts/parity_pulse_emit.sh" "$WORKSPACE_ROOT/bitpod-tools/scripts/parity_pulse_emit.sh"

  cat > "$CONTRACT_FILE" <<'EOF'
version = 1
status = "canonical"
contract_id = "local-workspace-skeleton"

[profile_aliases]
personal_full = "personal_machine_full"

[profiles.personal_machine_full]
required_paths = [
  "local-working-files",
  "local-trash-delete",
  "local-trash-delete/local-purge",
  "local-personal-only",
]
optional_paths = []
disabled_paths = [
  "local-codex",
  "local-handoffs",
  "local-shared-dropoff",
]
EOF

  cat > "$ZONE_POLICY_FILE" <<'EOF'
# zone|mode|rel_path|notes
working|STRICT_CANONICAL|local-workspace/local-working-files|active working files
pm_only|REPORT_ONLY|local-workspace/local-personal-only|personal-only lane when enabled by profile
EOF

  create_tracked_repo "alpha"
  create_tracked_repo "beta"
  create_tracked_repo "delta"
  create_tracked_repo "demo-repository"

  git init -b main "$WORKSPACE_ROOT/gamma" >/dev/null
  echo "gamma" > "$WORKSPACE_ROOT/gamma/README.md"
  git_commit_all "$WORKSPACE_ROOT/gamma" "initial"

  echo "dirty change" >> "$WORKSPACE_ROOT/beta/README.md"
  advance_remote "delta"

  cat > "$REGISTRY_FILE" <<'EOF'
# repo|relative_path|pulse_enabled|cleanup_enabled|thread_visible|verified|notes
alpha|alpha|1|1|1|1|verified
beta|beta|1|1|1|1|verified
test-bitpod-tools|bitpod-tools|1|1|1|1|verified
delta|delta|1|1|1|1|verified
demo-repository|demo-repository|1|1|1|1|verified
gamma|gamma|1|1|1|1|verified
EOF

  cat > "$PERFECT_REGISTRY_FILE" <<'EOF'
# repo|relative_path|pulse_enabled|cleanup_enabled|thread_visible|verified|notes
alpha|alpha|1|1|1|1|verified
beta|beta|1|1|1|1|verified
test-bitpod-tools|bitpod-tools|1|1|1|1|verified
delta|delta|1|1|1|1|verified
demo-repository|demo-repository|1|1|1|1|verified
gamma|gamma|1|1|1|1|verified
EOF

  cat > "$HOOK_REGISTRY_FILE" <<'EOF'
# repo|relative_path|pulse_enabled|cleanup_enabled|thread_visible|verified|notes
alpha|alpha|1|1|1|1|verified
beta|beta|0|1|1|1|verified but pulse disabled
gamma|gamma|1|1|1|0|verification pending
EOF

  create_tracked_repo "bitpod-tools"
}

test_refresh_repo_registry() {
  local refresh_root="$TEST_ROOT/refresh_workspace"
  local refresh_config="$refresh_root/bitpod-tools/config"
  local refresh_registry="$refresh_config/repo_registry.tsv"

  mkdir -p "$refresh_config"
  git init -b main "$refresh_root/demo-repository" >/dev/null
  mkdir -p "$refresh_root/docs-candidate/.github"
  cat > "$refresh_registry" <<'EOF'
# repo|relative_path|pulse_enabled|cleanup_enabled|thread_visible|verified|notes
demo-repository|demo-repository|1|1|1|1|verified repo
EOF

  BITPOD_APP_ROOT="$refresh_root" \
  BITPOD_REPO_REGISTRY_FILE="$refresh_registry" \
  "$REFRESH_REGISTRY" >/dev/null

  local registry_contents
  registry_contents="$(cat "$refresh_registry")"
  assert_contains "$registry_contents" "demo-repository|demo-repository|1|1|1|1|verified repo"
  assert_contains "$registry_contents" "docs-candidate|docs-candidate|0|0|0|0|candidate discovered via .github only; verify manually before enabling"
}

test_cleanup_contracts() {
  local t1_output
  t1_output="$(run_audit_capture "$REGISTRY_FILE" "run audit only repos")"
  assert_contains "$t1_output" "Audit Control | T1 Cleanup"
  assert_contains "$t1_output" "- result=NOT VERIFIED"
  assert_contains "$t1_output" "- overall=NOT VERIFIED"
  assert_contains "$t1_output" "- repo_scope=skipped"
  assert_contains "$t1_output" "- repo_findings=skipped_for_t1"
  assert_not_contains "$t1_output" "LIKELY MATCH"
  assert_not_contains "$t1_output" "LOCAL DIVERGED"
  assert_not_contains "$t1_output" "UNLINKED"
  assert_not_contains "$t1_output" "REMOTE MISMATCH"
  assert_contains "$t1_output" "Local workspace checks were suppressed for this run."

  local t2_output
  t2_output="$(run_audit_capture "$REGISTRY_FILE" "run T2 cleanup audit only repos")"
  assert_contains "$t2_output" "Audit Control | T2 Cleanup"
  assert_contains "$t2_output" "- result=NOT VERIFIED"
  assert_contains "$t2_output" "- overall=NOT VERIFIED"

  local t3_output=""
  local t3_status=0
  if t3_output="$(run_audit_capture "$REGISTRY_FILE" "run T3 audit only repos")"; then
    t3_status=0
  else
    t3_status=$?
  fi
  [[ "$t3_status" -eq 30 ]] || fail "expected fractured T3 exit status 30, got $t3_status"
  assert_contains "$t3_output" "Audit Control | T3 Cleanup"
  assert_contains "$t3_output" "- result=FRACTURED"
  assert_contains "$t3_output" "- overall=VERIFIED"
  assert_contains "$t3_output" "REMOTE MISMATCH"
  assert_contains "$t3_output" "- stale_local_codex_branches=0"
  assert_contains "$t3_output" "- stale_remote_codex_branches=0"
  assert_contains "$t3_output" "- open_pull_requests=0"
  assert_contains "$t3_output" "Cleanup remains fractured"

  local porcelain_output
  make_workspace_fully_clean
  porcelain_output="$(run_audit_capture "$PERFECT_REGISTRY_FILE" "run T3 audit only repos")"
  restore_dirty_workspace_shape
  assert_contains "$porcelain_output" "- result=PORCELAIN"
  assert_contains "$porcelain_output" "- overall=VERIFIED"
  assert_contains "$porcelain_output" "- stale_local_codex_branches=0"
  assert_contains "$porcelain_output" "- stale_remote_codex_branches=0"
  assert_contains "$porcelain_output" "- open_pull_requests=0"
  assert_contains "$porcelain_output" "- repo_findings=none"
}

test_stale_branch_contracts() {
  make_workspace_fully_clean
  git -C "$WORKSPACE_ROOT/alpha" checkout -b codex/stale-branch >/dev/null
  git -C "$WORKSPACE_ROOT/alpha" checkout main >/dev/null
  git -C "$WORKSPACE_ROOT/alpha" push origin codex/stale-branch >/dev/null

  local stale_output=""
  local stale_status=0
  if stale_output="$(run_audit_capture "$PERFECT_REGISTRY_FILE" "run T3 audit only repos")"; then
    stale_status=0
  else
    stale_status=$?
  fi
  [[ "$stale_status" -eq 30 ]] || fail "expected stale-branch T3 exit status 30, got $stale_status"
  assert_contains "$stale_output" "- result=FRACTURED"
  assert_contains "$stale_output" "- overall=NOT VERIFIED"
  assert_contains "$stale_output" "- stale_local_codex_branches=1"
  assert_contains "$stale_output" "- stale_remote_codex_branches=1"
  assert_contains "$stale_output" "- stale_ref=alpha scope=local ref=codex/stale-branch"
  assert_contains "$stale_output" "- stale_ref=alpha scope=remote ref=origin/codex/stale-branch"

  git -C "$WORKSPACE_ROOT/alpha" push origin --delete codex/stale-branch >/dev/null
  git -C "$WORKSPACE_ROOT/alpha" branch -D codex/stale-branch >/dev/null
  restore_dirty_workspace_shape
}

test_open_pr_remote_branch_is_not_stale() {
  make_workspace_fully_clean
  local fake_bin="$TEST_ROOT/fake_bin"
  mkdir -p "$fake_bin"

  git -C "$WORKSPACE_ROOT/alpha" checkout -b codex/open-pr >/dev/null
  git -C "$WORKSPACE_ROOT/alpha" push origin codex/open-pr >/dev/null
  git -C "$WORKSPACE_ROOT/alpha" checkout main >/dev/null
  git -C "$WORKSPACE_ROOT/alpha" branch -D codex/open-pr >/dev/null

  cat > "$fake_bin/gh" <<'EOF'
#!/usr/bin/env bash
if [[ "$*" == *"BitPod-App/alpha"* ]]; then
  printf '%s\n' '[{"number":7,"headRefName":"codex/open-pr","url":"https://example.test/pr/7"}]'
else
  printf '%s\n' '[]'
fi
EOF
  chmod +x "$fake_bin/gh"

  local pr_output
  pr_output="$(run_audit_capture_with_path "$PERFECT_REGISTRY_FILE" "run T3 audit only repos" "$fake_bin")"
  assert_contains "$pr_output" "- result=PORCELAIN"
  assert_contains "$pr_output" "- overall=VERIFIED"
  assert_contains "$pr_output" "- stale_remote_codex_branches=0"
  assert_contains "$pr_output" "- open_pull_requests=1"
  assert_contains "$pr_output" "- open_pr=alpha number=7 head=codex/open-pr url=https://example.test/pr/7"

  git -C "$WORKSPACE_ROOT/alpha" push origin --delete codex/open-pr >/dev/null
  restore_dirty_workspace_shape
}

test_top_level_workspace_truth_contracts() {
  make_workspace_fully_clean
  create_tracked_repo "zeta"
  create_linked_worktree_repo "eta"
  create_linked_worktree_repo "theta"
  local worktree_registry="$TEST_ROOT/perfect_registry_with_worktree.tsv"
  cp "$PERFECT_REGISTRY_FILE" "$worktree_registry"
  echo "theta|theta|1|1|1|1|verified linked worktree" >> "$worktree_registry"
  mkdir -p "$WORKSPACE_ROOT/T01-Agents"
  ln -s alpha "$WORKSPACE_ROOT/taylor01-skills"
  printf 'stray\n' > "$WORKSPACE_ROOT/stray-root.txt"
  mkdir -p "$WORKSPACE_ROOT/bitpod-docs/process"
  cat > "$WORKSPACE_ROOT/bitpod-docs/process/global-agent-policy-distribution-manifest.json" <<'EOF'
{
  "activeRepos": [
    "alpha",
    "beta",
    "delta",
    "demo-repository",
    "gamma",
    "ghost-repo"
  ]
}
EOF

  local truth_output=""
  local truth_status=0
  if truth_output="$(run_audit_capture "$worktree_registry" "run T3 audit only repos")"; then
    truth_status=0
  else
    truth_status=$?
  fi

  [[ "$truth_status" -eq 30 ]] || fail "expected top-level truth T3 exit status 30, got $truth_status"
  assert_contains "$truth_output" "- result=FRACTURED"
  assert_contains "$truth_output" "- registry_problem=zeta problem=UNREGISTERED_TOP_LEVEL_GIT_REPO detail=zeta"
  assert_contains "$truth_output" "- registry_problem=eta problem=UNREGISTERED_TOP_LEVEL_GIT_REPO detail=eta"
  assert_not_contains "$truth_output" "registry_problem=theta problem=NOT_GIT_REPO"
  assert_contains "$truth_output" "- top_level_finding=PROHIBITED_TOP_LEVEL_FOLDER path=T01-Agents blocking=true"
  assert_contains "$truth_output" "- top_level_finding=PROHIBITED_TOP_LEVEL_SYMLINK path=taylor01-skills blocking=true"
  assert_contains "$truth_output" "- top_level_finding=PROHIBITED_TOP_LEVEL_FILE path=stray-root.txt blocking=true"
  assert_not_contains "$truth_output" "- top_level_finding=PROHIBITED_TOP_LEVEL_FOLDER path=eta"
  assert_not_contains "$truth_output" "- top_level_finding=PROHIBITED_TOP_LEVEL_FOLDER path=theta"
  assert_contains "$truth_output" "- stale_manifest_warning=MANIFEST_OMITS_TOP_LEVEL_GIT_REPO repo=zeta"
  assert_contains "$truth_output" "- stale_manifest_warning=MANIFEST_OMITS_TOP_LEVEL_GIT_REPO repo=eta"
  assert_contains "$truth_output" "- stale_manifest_warning=MANIFEST_ACTIVE_REPO_MISSING_LOCAL_GIT repo=ghost-repo"

  git -C "$TEST_ROOT/eta_source" worktree remove --force "$WORKSPACE_ROOT/eta" >/dev/null
  git -C "$TEST_ROOT/theta_source" worktree remove --force "$WORKSPACE_ROOT/theta" >/dev/null
  rm -rf "$WORKSPACE_ROOT/zeta" "$REMOTE_ROOT/zeta.git" "$REMOTE_ROOT/eta.git" "$REMOTE_ROOT/theta.git" "$WORKSPACE_ROOT/T01-Agents" "$WORKSPACE_ROOT/taylor01-skills" "$WORKSPACE_ROOT/stray-root.txt" "$WORKSPACE_ROOT/bitpod-docs"
  restore_dirty_workspace_shape
}

test_manifest_drift_is_not_verified() {
  make_workspace_fully_clean
  create_tracked_repo "bitpod-docs"
  local manifest_registry="$TEST_ROOT/perfect_registry_with_manifest_repo.tsv"
  cp "$PERFECT_REGISTRY_FILE" "$manifest_registry"
  echo "bitpod-docs|bitpod-docs|1|1|1|1|verified manifest repo" >> "$manifest_registry"
  mkdir -p "$WORKSPACE_ROOT/bitpod-docs/process"
  cat > "$WORKSPACE_ROOT/bitpod-docs/process/global-agent-policy-distribution-manifest.json" <<'EOF'
{
  "activeRepos": [
    "alpha",
    "bitpod-docs",
    "bitpod-tools",
    "delta",
    "demo-repository",
    "gamma"
  ]
}
EOF

  local manifest_output=""
  local manifest_status=0
  if manifest_output="$(run_audit_capture "$manifest_registry" "run T3 audit only repos")"; then
    manifest_status=0
  else
    manifest_status=$?
  fi

  [[ "$manifest_status" -eq 30 ]] || fail "expected manifest drift T3 exit status 30, got $manifest_status"
  assert_contains "$manifest_output" "- result=FRACTURED"
  assert_contains "$manifest_output" "- overall=NOT VERIFIED"
  assert_contains "$manifest_output" "- registry_problems=0"
  assert_contains "$manifest_output" "- top_level_blocking_findings=0"
  assert_contains "$manifest_output" "- stale_manifest_warning=MANIFEST_OMITS_TOP_LEVEL_GIT_REPO repo=beta"

  rm -rf "$WORKSPACE_ROOT/bitpod-docs" "$REMOTE_ROOT/bitpod-docs.git"
  restore_dirty_workspace_shape
}

test_parity_pulse_contracts() {
  local pulse_output
  pulse_output="$(run_audit_capture "$REGISTRY_FILE" "__parity_pulse__ event=post-commit fresh")"
  assert_contains "$pulse_output" "Parity Pulse"
  assert_contains "$pulse_output" "- event=post-commit"
  assert_contains "$pulse_output" "- result=REPORT ONLY"
  assert_contains "$pulse_output" "- verification=VERIFIED"
  assert_contains "$pulse_output" "LOCAL DIVERGED"
  assert_contains "$pulse_output" "REMOTE MISMATCH"
  assert_contains "$pulse_output" "UNLINKED"
  assert_not_contains "$pulse_output" "Local workspace"
  assert_not_contains "$pulse_output" "alpha@main"

  local perfect_pulse
  make_workspace_fully_clean
  perfect_pulse="$(run_audit_capture "$PERFECT_REGISTRY_FILE" "__parity_pulse__ event=pre-push fresh")"
  restore_dirty_workspace_shape
  assert_contains "$perfect_pulse" "- result=PORCELAIN"
  assert_contains "$perfect_pulse" "- verification=VERIFIED"
  assert_contains "$perfect_pulse" "- repo_findings=none"

  local unverified_perfect_shape
  make_workspace_fully_clean
  unverified_perfect_shape="$(run_audit_capture "$PERFECT_REGISTRY_FILE" "__parity_pulse__ event=post-commit")"
  restore_dirty_workspace_shape
  assert_contains "$unverified_perfect_shape" "- result=REPORT ONLY"
  assert_contains "$unverified_perfect_shape" "- verification=NOT VERIFIED"
  assert_not_contains "$unverified_perfect_shape" "- result=PORCELAIN"

  local dirs_before
  dirs_before="$(find "$WORKSPACE_ROOT/local-workspace/local-working-files" -mindepth 1 -maxdepth 1 -type d | wc -l | tr -d ' ')"
  local emitted_pulse
  make_workspace_fully_clean
  emitted_pulse="$(run_pulse_emit "$PERFECT_REGISTRY_FILE" "pre-push" "$WORKSPACE_ROOT/alpha")"
  restore_dirty_workspace_shape
  local dirs_after
  dirs_after="$(find "$WORKSPACE_ROOT/local-workspace/local-working-files" -mindepth 1 -maxdepth 1 -type d | wc -l | tr -d ' ')"
  assert_contains "$emitted_pulse" "Parity Pulse"
  assert_equals "$dirs_before" "$dirs_after"
}

test_hook_installer() {
  BITPOD_APP_ROOT="$WORKSPACE_ROOT" \
  BITPOD_REPO_REGISTRY_FILE="$HOOK_REGISTRY_FILE" \
  "$INSTALL_HOOKS" >/dev/null

  assert_file_exists "$WORKSPACE_ROOT/alpha/.git/hooks/post-commit"
  assert_file_exists "$WORKSPACE_ROOT/alpha/.git/hooks/pre-push"
  assert_file_missing "$WORKSPACE_ROOT/beta/.git/hooks/post-commit"
  assert_file_missing "$WORKSPACE_ROOT/gamma/.git/hooks/post-commit"
}

test_scheduled_cleanup_helper() {
  local scheduled_output
  make_workspace_fully_clean
  scheduled_output="$(run_scheduled_capture "$PERFECT_REGISTRY_FILE")"
  restore_dirty_workspace_shape
  assert_contains "$scheduled_output" "- result=PORCELAIN"
  assert_file_exists "$WORKSPACE_ROOT/local-workspace/local-working-files/local-cleanup-audit/latest_scheduled_cleanup.md"
  assert_file_exists "$WORKSPACE_ROOT/local-workspace/local-working-files/local-cleanup-audit/scheduled_cleanup_state.env"

  local state_contents
  state_contents="$(cat "$WORKSPACE_ROOT/local-workspace/local-working-files/local-cleanup-audit/scheduled_cleanup_state.env")"
  assert_contains "$state_contents" "consecutive_failures=0"
  assert_contains "$state_contents" "last_result=\"PORCELAIN\""

  local fractured_output=""
  fractured_output="$(run_scheduled_capture "$REGISTRY_FILE" || true)"
  assert_contains "$fractured_output" "- result=FRACTURED"
  state_contents="$(cat "$WORKSPACE_ROOT/local-workspace/local-working-files/local-cleanup-audit/scheduled_cleanup_state.env")"
  assert_contains "$state_contents" "consecutive_failures=1"
  assert_contains "$state_contents" "last_result=\"FRACTURED\""

  local payload_contents
  payload_contents="$(cat "$WORKSPACE_ROOT/local-workspace/local-working-files/local-cleanup-audit/latest_linear_escalation.md")"
  assert_contains "$payload_contents" "- issue_kind: Chore"
  assert_contains "$payload_contents" "- issue_priority: low"
}

test_contract_derived_local_workspace_guardrails() {
  make_workspace_fully_clean
  mkdir -p "$WORKSPACE_ROOT/local-workspace/local-handoffs"
  echo "handoff residue" > "$WORKSPACE_ROOT/local-workspace/local-handoffs/test.txt"

  local guardrail_output=""
  local guardrail_status=0
  if guardrail_output="$(run_audit_capture "$PERFECT_REGISTRY_FILE" "run T3 audit")"; then
    guardrail_status=0
  else
    guardrail_status=$?
  fi

  [[ "$guardrail_status" -eq 30 ]] || fail "expected local-workspace guardrail T3 exit status 30, got $guardrail_status"
  assert_contains "$guardrail_output" "- result=FRACTURED"
  assert_contains "$guardrail_output" "- local_workspace_status=FAIL"
  assert_contains "$guardrail_output" "- unexpected_local_workspace_children=1"
  assert_contains "$guardrail_output" "- handoff_files=1"

  rm -rf "$WORKSPACE_ROOT/local-workspace/local-handoffs"
  restore_dirty_workspace_shape
}

test_local_trash_bucket_actionability_is_t1_t2_visible() {
  local bucket="$WORKSPACE_ROOT/local-workspace/local-trash-delete/local-high-volume-residue"
  mkdir -p "$bucket"
  for i in $(seq 1 101); do
    printf 'residue %s\n' "$i" > "$bucket/file-$i.txt"
  done

  local t1_output=""
  local t1_status=0
  if t1_output="$(run_audit_capture "$PERFECT_REGISTRY_FILE" "run audit")"; then
    t1_status=0
  else
    t1_status=$?
  fi
  [[ "$t1_status" -eq 0 ]] || fail "expected report-only trash bucket T1 exit status 0, got $t1_status"
  assert_contains "$t1_output" "- trash_actionable_buckets=1"
  assert_contains "$t1_output" "- trash_bucket=local-workspace/local-trash-delete/local-high-volume-residue action=review_for_local_purge files=101"
  assert_contains "$t1_output" "- files_to_move_to_local_purge=101"
  assert_contains "$t1_output" "Do you want me to execute and move the identified eligible items to the approved trash/disposal lane, yes or no?"
  assert_contains "$t1_output" "run T1 cleanup execute local-workspace"

  local t2_output=""
  local t2_status=0
  make_workspace_fully_clean
  if t2_output="$(run_audit_capture "$PERFECT_REGISTRY_FILE" "run T2 audit")"; then
    t2_status=0
  else
    t2_status=$?
  fi
  [[ "$t2_status" -eq 20 ]] || fail "expected trash bucket T2 exit status 20, got $t2_status"
  assert_contains "$t2_output" "- trash_actionable_buckets=1"
  assert_contains "$t2_output" "- quick_gate=ESCALATE_RECOMMENDED"
  assert_contains "$t2_output" "- medium_gate=ESCALATE_RECOMMENDED"
  assert_contains "$t2_output" "Do you want me to execute and move the identified eligible items to the approved trash/disposal lane, yes or no?"
  restore_dirty_workspace_shape

  rm -rf "$bucket"
}

test_t1_safe_local_workspace_execute_moves_to_local_purge() {
  local bucket="$WORKSPACE_ROOT/local-workspace/local-trash-delete/local-execute-residue"
  mkdir -p "$bucket"
  printf 'residue\n' > "$bucket/file.txt"
  touch -t 202001010000 "$bucket/file.txt"

  local execute_output
  execute_output="$(run_audit_capture "$PERFECT_REGISTRY_FILE" "run T1 cleanup execute local-workspace")"
  assert_contains "$execute_output" "Audit Control | T1 Cleanup"
  assert_contains "$execute_output" "- trash_actionable_buckets=0"
  assert_file_missing "$bucket/file.txt"
  assert_file_exists "$WORKSPACE_ROOT/local-workspace/local-trash-delete/local-purge/local-execute-residue/file.txt"

  rm -rf "$WORKSPACE_ROOT/local-workspace/local-trash-delete/local-purge/local-execute-residue"
}

test_weekly_cleanup_moves_from_local_working_files_to_local_purge() {
  local weekly_root="$TEST_ROOT/weekly-cleanup-root"
  local src_dir="$weekly_root/local-workspace/local-working-files/weekly-trash-source"
  local dst_file="$weekly_root/local-workspace/local-trash-delete/local-purge/weekly-trash-source/file.txt"

  mkdir -p "$src_dir"
  printf 'weekly residue\n' > "$src_dir/file.txt"
  touch -t 202001010000 "$src_dir/file.txt"

  local weekly_output
  weekly_output="$(BITPOD_APP_ROOT="$weekly_root" "$AUDIT_CTL" "__cleanup_trash_weekly__")"

  assert_contains "$weekly_output" "Audit Control | Weekly Local Trash-to-Purge Cleanup"
  assert_contains "$weekly_output" "- scope=local-workspace/local-working-files -> local-workspace/local-trash-delete/local-purge"
  assert_contains "$weekly_output" "- final_status=mutated"
  assert_file_missing "$src_dir/file.txt"
  assert_file_exists "$dst_file"

  rm -rf "$weekly_root"
}

test_bounded_network_probes() {
  make_workspace_fully_clean
  local fake_bin="$TEST_ROOT/fake-bin"
  mkdir -p "$fake_bin"
  cat > "$fake_bin/gh" <<'EOF'
#!/usr/bin/env bash
sleep 2
echo '[]'
EOF
  chmod +x "$fake_bin/gh"

  local timed_output=""
  local timed_status=0
  if timed_output="$(run_audit_capture_with_path "$PERFECT_REGISTRY_FILE" "run T3 audit only repos" "$fake_bin")"; then
    timed_status=0
  else
    timed_status=$?
  fi

  [[ "$timed_status" -eq 30 ]] || fail "expected timed T3 exit status 30, got $timed_status"
  assert_contains "$timed_output" "- result=FRACTURED"
  assert_contains "$timed_output" "- overall=NOT VERIFIED"
  assert_contains "$timed_output" "- network_probe_failures=6"
  assert_contains "$timed_output" "network_probe_failure=surface=repo_audit repo=alpha operation=gh_pr_list detail=timed out after 1s"
  assert_contains "$timed_output" "network_probe_failure=surface=repo_audit repo=demo-repository operation=gh_pr_list detail=timed out after 1s"
  restore_dirty_workspace_shape
}

setup_workspace
test_refresh_repo_registry
test_cleanup_contracts
test_stale_branch_contracts
test_open_pr_remote_branch_is_not_stale
test_top_level_workspace_truth_contracts
test_manifest_drift_is_not_verified
test_parity_pulse_contracts
test_hook_installer
test_scheduled_cleanup_helper
test_contract_derived_local_workspace_guardrails
test_local_trash_bucket_actionability_is_t1_t2_visible
test_t1_safe_local_workspace_execute_moves_to_local_purge
test_weekly_cleanup_moves_from_local_working_files_to_local_purge
test_bounded_network_probes

echo "PASS: test_audit_tools.sh"
