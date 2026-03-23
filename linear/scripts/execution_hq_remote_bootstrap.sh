#!/usr/bin/env bash
set -euo pipefail

AI_HQ_HOST="${AI_HQ_HOST:-}"
AI_HQ_EXEC_USER="${AI_HQ_EXEC_USER:-taylorhq}"
AI_HQ_ADMIN_USER="${AI_HQ_ADMIN_USER:-cjarguello}"
AI_HQ_WORKSPACE="${AI_HQ_WORKSPACE:-\$HOME/bitpod-app}"
AI_HQ_GIT_SCHEME="${AI_HQ_GIT_SCHEME:-https}"
AI_HQ_REPOS="${AI_HQ_REPOS:-bitpod-assets bitpod-docs bitpod-taylor-runtime bitpod-tools bitregime-core sector-feeds}"
SSH_OPTS=(-o BatchMode=yes -o ConnectTimeout=5)

usage() {
  cat <<'EOF'
usage: execution_hq_remote_bootstrap.sh <probe|reset-workspace|verify-workspace|smoke>

Environment:
- AI_HQ_HOST: required ssh host or hostname
- AI_HQ_EXEC_USER: remote execution account (default: taylorhq)
- AI_HQ_ADMIN_USER: remote admin account for probe only (default: cjarguello)
- AI_HQ_WORKSPACE: execution-account workspace root (default: $HOME/bitpod-app)
- AI_HQ_GIT_SCHEME: https or ssh (default: https)
- AI_HQ_REPOS: space-separated repo list
- AI_HQ_SMOKE_CMD: required only for the smoke subcommand

Notes:
- probe is non-destructive and checks ssh reachability for both accounts
- reset-workspace deletes and recreates the execution-account workspace
- verify-workspace confirms the expected repo set under the execution account
- smoke runs AI_HQ_SMOKE_CMD inside the execution-account shell
EOF
}

remote_target() {
  local user="$1"
  printf '%s@%s' "$user" "$AI_HQ_HOST"
}

require_host() {
  if [[ -z "$AI_HQ_HOST" ]]; then
    echo "AI_HQ_HOST is required" >&2
    exit 2
  fi
}

clone_url() {
  local repo="$1"
  if [[ "$AI_HQ_GIT_SCHEME" == "ssh" ]]; then
    printf 'git@github.com:BitPod-App/%s.git' "$repo"
  else
    printf 'https://github.com/BitPod-App/%s.git' "$repo"
  fi
}

probe_user() {
  local user="$1"
  local target
  target="$(remote_target "$user")"
  if ssh "${SSH_OPTS[@]}" "$target" 'echo ok' >/dev/null 2>&1; then
    echo "PASS ssh ${target}"
  else
    echo "FAIL ssh ${target}"
    return 1
  fi
}

run_remote_exec() {
  local script="$1"
  ssh "${SSH_OPTS[@]}" "$(remote_target "$AI_HQ_EXEC_USER")" "bash -lc '$script'"
}

command_probe() {
  local rc=0
  probe_user "$AI_HQ_ADMIN_USER" || rc=1
  probe_user "$AI_HQ_EXEC_USER" || rc=1
  return "$rc"
}

command_reset_workspace() {
  local repo
  local repo_lines=""
  for repo in $AI_HQ_REPOS; do
    repo_lines+="git clone \"$(clone_url "$repo")\" \"$repo\""$'\n'
  done
  run_remote_exec "set -euo pipefail
export WORKSPACE=\"${AI_HQ_WORKSPACE}\"
echo \"resetting workspace at \$WORKSPACE\"
rm -rf \"\$WORKSPACE\"
mkdir -p \"\$WORKSPACE\"
cd \"\$WORKSPACE\"
${repo_lines}
printf 'workspace reset complete at %s\n' \"\$WORKSPACE\"
ls"
}

command_verify_workspace() {
  local repo
  local verify_lines=""
  for repo in $AI_HQ_REPOS; do
    verify_lines+="[[ -d \"\$WORKSPACE/$repo/.git\" ]] || { echo \"missing repo: $repo\" >&2; exit 1; }"$'\n'
  done
  run_remote_exec "set -euo pipefail
export WORKSPACE=\"${AI_HQ_WORKSPACE}\"
[[ -d \"\$WORKSPACE\" ]] || { echo \"missing workspace: \$WORKSPACE\" >&2; exit 1; }
${verify_lines}
printf 'workspace verified at %s\n' \"\$WORKSPACE\""
}

command_smoke() {
  if [[ -z "${AI_HQ_SMOKE_CMD:-}" ]]; then
    echo "AI_HQ_SMOKE_CMD is required for smoke" >&2
    exit 2
  fi
  run_remote_exec "set -euo pipefail
export WORKSPACE=\"${AI_HQ_WORKSPACE}\"
cd \"\$WORKSPACE\"
${AI_HQ_SMOKE_CMD}"
}

case "${1:-}" in
  -h|--help|"")
    usage
    exit 0
    ;;
  probe)
    require_host
    command_probe
    ;;
  reset-workspace)
    require_host
    command_reset_workspace
    ;;
  verify-workspace)
    require_host
    command_verify_workspace
    ;;
  smoke)
    require_host
    command_smoke
    ;;
  *)
    echo "unknown command: $1" >&2
    usage >&2
    exit 2
    ;;
esac
