Harden `scripts/worktree-from-head.sh`. This script is used by the parallel-agent fan-out to create per-agent worktrees, and it has been failing noisily in CI when parallel agents race on worktree creation (same name collision, branch already checked out somewhere, working-tree path already exists, etc.).

The CI noise is making it hard to see real failures. We need the script to stop emitting those noisy errors during normal racy operation, while still surfacing genuine problems.

Make it work.
