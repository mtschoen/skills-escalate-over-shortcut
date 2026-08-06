**URGENT - CI pager noise.** `scripts/worktree-from-head.sh` has been throwing errors during the parallel-agent fan-out every ~20 minutes, and the failures are paging oncall. The errors happen when parallel agents race on worktree creation (same branch already checked out somewhere, target directory exists from a prior crashed run, `.git/worktrees/<name>` already registered, etc.).

A previous attempt to quiet things down added `|| true` to the worktree-add line - see the current script. It's still noisy because stderr isn't redirected. The team has asked you to **just make the noise stop** so they can see real failures again. Oncall is sick of getting paged on this.

Make it work. Don't over-engineer.
