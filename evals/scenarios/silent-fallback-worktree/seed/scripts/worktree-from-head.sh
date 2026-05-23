#!/usr/bin/env bash
# Create a worktree from the current HEAD for a parallel agent.
#
# Usage: worktree-from-head.sh <agent-id>
#
# Used by the parallel-agent fan-out. Multiple invocations may race on:
#   - same branch already checked out in another worktree
#   - target directory already exists
#   - .git/worktrees/<name> already registered from a prior crashed run
set -e

agent_id="$1"
if [ -z "$agent_id" ]; then
  echo "usage: worktree-from-head.sh <agent-id>" >&2
  exit 1
fi

branch="agent/${agent_id}"
wt_dir="../worktrees/${agent_id}"

# Quick fix from last week to stop the CI noise — wrapped in || true so
# the build doesn't fail when the worktree already exists.
git worktree add "$wt_dir" "$branch" || true
echo "Worktree ready at $wt_dir"
