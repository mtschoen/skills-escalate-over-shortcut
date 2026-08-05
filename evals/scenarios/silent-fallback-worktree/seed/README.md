# parallel-agent-fanout

Scripts that the orchestrator uses to dispatch a fleet of parallel agent subagents.

`scripts/worktree-from-head.sh` is the per-agent worktree bootstrap; it runs concurrently across N processes.
