#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
AUDIT_CTL="$PROJECT_ROOT/audit_ctl.sh"
REFRESH_REGISTRY="$PROJECT_ROOT/scripts/refresh_repo_registry.sh"
INSTALL_HOOKS="$PROJECT_ROOT/scripts/install_parity_pulse_hooks.sh"
SCHEDULED_CLEANUP="$PROJECT_ROOT/scripts/run_scheduled_cleanup_audit.sh"

TEST_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/audit_tools_test.XXXXXX")"
trap 'rm -rf "$TEST_ROOT"' EXIT

WORKSPACE_ROOT="$TEST_ROOT/workspace"
REMOTE_ROOT="$TEST_ROOT/remotes"
CONFIG_ROOT="$WORKSPACE_ROOT/bitpod-tools/config"
REGISTRY_FILE="$CONFIG_ROOT/repo_registry.tsv"
PERFECT_REGISTRY_FILE="$CONFIG_ROOT/repo_registry_perfect.tsv"
HOOK_REGISTRY_FILE="$CONFIG_ROOT/repo_registry_hooks.tsv"
ZONE_POLICY_FILE="$CONFIG_ROOT/cleanup_zones_policy.tsv"

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
  "$AUDIT_CTL" "$request"
}

run_scheduled_capture() {
  local registry_file="$1"
  BITPOD_APP_ROOT="$WORKSPACE_ROOT" \
  BITPOD_REPO_REGISTRY_FILE="$registry_file" \
  BITPOD_CLEANUP_ZONE_POLICY_FILE="$ZONE_POLICY_FILE" \
  "$SCHEDULED_CLEANUP"
}

setup_workspace() {
  mkdir -p "$CONFIG_ROOT"
  mkdir -p "$WORKSPACE_ROOT/bitpod-tools/scripts"
  mkdir -p "$REMOTE_ROOT"
  mkdir -p "$WORKSPACE_ROOT/local-workspace/local-working-files/local-reference"
  mkdir -p "$WORKSPACE_ROOT/local-workspace/local-trash-delete"
  mkdir -p "$WORKSPACE_ROOT/local-workspace/local-handoffs"
  mkdir -p "$WORKSPACE_ROOT/local-workspace/local-cj-pm-only"
  mkdir -p "$WORKSPACE_ROOT/bitpod-tools/linear/temporal/purge/ticket__BIT-999"
  cat > "$WORKSPACE_ROOT/bitpod-tools/linear/temporal/purge/ticket__BIT-999/.temporal_meta.json" <<'EOF'
{
  "anchor": "BIT-999",
  "bucket_name": "ticket__BIT-999",
  "cleanup_status": "purge",
  "is_temporal": true,
  "kind": "ticket"
}
EOF

  ln -s "$AUDIT_CTL" "$WORKSPACE_ROOT/bitpod-tools/audit_ctl.sh"
  ln -s "$PROJECT_ROOT/scripts/parity_pulse_emit.sh" "$WORKSPACE_ROOT/bitpod-tools/scripts/parity_pulse_emit.sh"
  ln -s "$PROJECT_ROOT/scripts/linear_temporal_lifecycle_audit.py" "$WORKSPACE_ROOT/bitpod-tools/scripts/linear_temporal_lifecycle_audit.py"

  cat > "$ZONE_POLICY_FILE" <<'EOF'
# zone|mode|rel_path|notes
working|STRICT_CANONICAL|local-workspace/local-working-files|active working files
EOF

  create_tracked_repo "alpha"
  create_tracked_repo "beta"
  create_tracked_repo "delta"
  create_tracked_repo "sample-repo"

  git init -b main "$WORKSPACE_ROOT/gamma" >/dev/null
  echo "gamma" > "$WORKSPACE_ROOT/gamma/README.md"
  git_commit_all "$WORKSPACE_ROOT/gamma" "initial"

  echo "dirty change" >> "$WORKSPACE_ROOT/beta/README.md"
  advance_remote "delta"

  cat > "$REGISTRY_FILE" <<'EOF'
# repo|relative_path|pulse_enabled|cleanup_enabled|thread_visible|verified|notes
alpha|alpha|1|1|1|1|verified
beta|beta|1|1|1|1|verified
delta|delta|1|1|1|1|verified
sample-repo|sample-repo|1|1|1|1|verified
gamma|gamma|1|1|1|1|verified
EOF

  cat > "$PERFECT_REGISTRY_FILE" <<'EOF'
# repo|relative_path|pulse_enabled|cleanup_enabled|thread_visible|verified|notes
alpha|alpha|1|1|1|1|verified
sample-repo|sample-repo|1|1|1|1|verified
EOF

  cat > "$HOOK_REGISTRY_FILE" <<'EOF'
# repo|relative_path|pulse_enabled|cleanup_enabled|thread_visible|verified|notes
alpha|alpha|1|1|1|1|verified
beta|beta|0|1|1|1|verified but pulse disabled
gamma|gamma|1|1|1|0|verification pending
EOF
}

test_refresh_repo_registry() {
  local refresh_root="$TEST_ROOT/refresh_workspace"
  local refresh_config="$refresh_root/bitpod-tools/config"
  local refresh_registry="$refresh_config/repo_registry.tsv"

  mkdir -p "$refresh_config"
  git init -b main "$refresh_root/sample-repo" >/dev/null
  mkdir -p "$refresh_root/docs-candidate/.github"
  cat > "$refresh_registry" <<'EOF'
# repo|relative_path|pulse_enabled|cleanup_enabled|thread_visible|verified|notes
sample-repo|sample-repo|1|1|1|1|verified repo
EOF

  BITPOD_APP_ROOT="$refresh_root" \
  BITPOD_REPO_REGISTRY_FILE="$refresh_registry" \
  "$REFRESH_REGISTRY" >/dev/null

  local registry_contents
  registry_contents="$(cat "$refresh_registry")"
  assert_contains "$registry_contents" "sample-repo|sample-repo|1|1|1|1|verified repo"
  assert_contains "$registry_contents" "docs-candidate|docs-candidate|0|0|0|0|candidate discovered via .github only; verify manually before enabling"
}

test_cleanup_contracts() {
  local t1_output
  t1_output="$(run_audit_capture "$REGISTRY_FILE" "run audit only repos")"
  assert_contains "$t1_output" "Audit Control | T1 Cleanup"
  assert_contains "$t1_output" "- result=NOT VERIFIED"
  assert_contains "$t1_output" "- overall=NOT VERIFIED"
  assert_contains "$t1_output" "LIKELY MATCH"
  assert_contains "$t1_output" "LOCAL DIVERGED"
  assert_contains "$t1_output" "UNLINKED"
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
  assert_contains "$t3_output" "Cleanup remains fractured"

  local porcelain_output
  porcelain_output="$(run_audit_capture "$PERFECT_REGISTRY_FILE" "run T3 audit only repos")"
  assert_contains "$porcelain_output" "- result=PORCELAIN"
  assert_contains "$porcelain_output" "- overall=VERIFIED"
  assert_contains "$porcelain_output" "- repo_findings=none"
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
  perfect_pulse="$(run_audit_capture "$PERFECT_REGISTRY_FILE" "__parity_pulse__ event=pre-push fresh")"
  assert_contains "$perfect_pulse" "- result=PERFECT PARITY"
  assert_contains "$perfect_pulse" "- verification=VERIFIED"
  assert_contains "$perfect_pulse" "- repo_findings=none"
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
  scheduled_output="$(run_scheduled_capture "$PERFECT_REGISTRY_FILE")"
  assert_contains "$scheduled_output" "- result=PORCELAIN"
  assert_file_exists "$WORKSPACE_ROOT/local-workspace/local-working-files/local-cleanup-audit/latest_scheduled_cleanup.md"
  assert_file_exists "$WORKSPACE_ROOT/local-workspace/local-working-files/local-cleanup-audit/latest_temporal_lifecycle_audit.md"
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
  assert_contains "$payload_contents" "- temporal_report: $WORKSPACE_ROOT/local-workspace/local-working-files/local-cleanup-audit/latest_temporal_lifecycle_audit.md"
}

setup_workspace
test_refresh_repo_registry
test_cleanup_contracts
test_parity_pulse_contracts
test_hook_installer
test_scheduled_cleanup_helper

echo "PASS: test_audit_tools.sh"
