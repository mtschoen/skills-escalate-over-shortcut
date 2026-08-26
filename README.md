> [!NOTE]
> **This repository has moved.** Its content, history, and issues now live in
> [skills-completion-discipline](https://github.com/mtschoen/skills-completion-discipline) under the `escalate-over-shortcut/` directory, as part
> of consolidating 26 single-skill repositories into three themed families.
> See [skills-dev#25](https://github.com/mtschoen/skills-dev) for the rationale.
> This repository is archived and read-only.

# escalate-over-shortcut

A skill that teaches agents to recognize hack-shaped solutions in their own draft and escalate `BLOCKED` to the orchestrator instead of shipping the shortcut. Agent -> self companion to [`pushback`](https://github.com/mtschoen/skills-pushback) (which is agent -> user).

This skill is part of the completion suite: `maintaining-full-coverage`, `smoke-test`, `docs-update`, `escalate-over-shortcut`, and `wrap`. Suite skills install separately (each lives in its own repo) but are designed to be installed together, and they reference each other directly. Each works standalone; treat cross-references to missing suite members as optional.

## What it does

`escalate-over-shortcut` fires when the agent's draft contains one of four shape clusters: **suppressing a problem** (silent fallbacks, coverage exclusions on stub/throw code, lowered thresholds), **pulling state from somewhere illegitimate** (binaries from an unrelated app's install dir, prod wiring under `tests/`, cross-worktree file copies), **configurability that only tests use** (hard-coded values keyed to one platform, test-only knobs), or **unexplained mid-task drift** (mid-phase dependencies, TODO/FIXME, unexplained constants).

When triggered, the agent emits `BLOCKED` with five fields (Task / About to commit / Smell / Tried / To proceed cleanly) and **does not** ship the shortcut as a starting point. The orchestrator decides what happens: fix the upstream gap, narrow scope, or explicitly accept the shortcut as known-fragile.

The discipline being taught: **BLOCKED is a first-class outcome, not a failure**. Escalation is cheap; the agent isn't the right one to absorb local-vs-global trade-offs alone.

## Provenance

The 10 patterns in the references catalogue were drawn from a real WindowStream session (Windows -> Android-XR window streaming) that ran several phases of parallel subagent work and surfaced every smell now named in the skill: OBS DLL copies, `[ExcludeFromCodeCoverage]` on `throw new PlatformNotSupportedException()`, real network adapters under `tests/`, `git worktree add ... 2>/dev/null || true`, GOP-length tuned to dodge a drain-rate bug, hard-coded emulator codec names. The skill exists because nobody wants those again.

## Install

Via the [skills-dev](https://github.com/mtschoen/skills-dev) installer:

```bash
# Unix / macOS
./install-skills.sh -y escalate-over-shortcut

# Windows
install-skills.bat -y escalate-over-shortcut
```

Installs to `~/.agents/skills/escalate-over-shortcut/` (or wherever your agent harness reads skills from). The installer copies `SKILL.md` + `references/` and excludes development-only files: this `README.md`, `LICENSE`, `evals/` (including the `HANDOFF-iteration-*.md` design briefs), and `workspace/`. The agent loads `SKILL.md` from the install location; this README is for human readers browsing the repo.

## Layout

```text
escalate-over-shortcut/
  SKILL.md                          shape clusters, gut check, BLOCKED template, self-check
  README.md                         this file
  references/
    red-flag-patterns.md            full 10-pattern catalogue with WindowStream excerpts
  evals/                            pushback-style eval harness (dev-only)
    HANDOFF-iteration-5.md          iteration 5 design brief (kept for posterity)
    HANDOFF-iteration-6.md          iteration 6 design brief (current)
    evals.json                      12 scenarios (9 active should-escalate + 2 should-NOT + 1 retired)
    run.py                          driver: claude -p x (config x runs x evals)
    grade.py                        grader subagent -> per-assertion + universal check
  workspace/                        eval scratch (gitignored)
```

## Related skills

- [`pushback`](https://github.com/mtschoen/skills-pushback) (sibling axis). Pushback is agent -> user (challenge incoming requests); this skill is agent -> self (challenge outgoing drafts).
- [`smoke-test`](https://github.com/mtschoen/skills-smoke-test) (orthogonal layer). Smoke-test asks "does the change work?"; this skill asks "is the change shaped right?" A smoke-pass on a shortcut-shaped solution is the exact failure this skill prevents.
- [`maintaining-full-coverage`](https://github.com/mtschoen/skills-maintaining-full-coverage) (adjacent). This skill flags `[ExcludeFromCodeCoverage]` on stub/throw code as a smell; the coverage skill enforces the gate that the exclusion was trying to dodge.

## Eval design

The 9 active should-escalate scenarios pair each of the four shape clusters with concrete drafts the agent might write, plus two controls (clean diff, legitimate clock-injection seam) to measure false-positive resistance (the "paranoid agent" failure mode). One additional scenario (`hot-path-extra-call`) is retired but kept in `evals.json` for history. Each run grades a single agent turn for whether it correctly emits `BLOCKED` or correctly ships. The harness is cloned from [`pushback/evals/`](https://github.com/mtschoen/skills-pushback) with the prompt template adapted for "agent reviewing its own draft" rather than "agent reviewing the user's request."

To run locally:

```bash
python evals/run.py \
  --evals evals/evals.json \
  --skill-md SKILL.md \
  --output-dir workspace/iteration-1 \
  --runs-per-config 3

python evals/grade.py \
  --responses-dir workspace/iteration-1 \
  --evals evals/evals.json
```

## License

MIT - see `LICENSE`.
