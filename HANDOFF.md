# Escalate Over Improvise — Skill Handoff

**Status:** Not yet built. This document briefs the agent who will create the skill. Companion to the existing `pushback` skill, which handles Claude→user pushback; this skill is agent→self: *recognize when the solution you're about to commit is a hack, and escalate BLOCKED instead of shipping it.*

**Tentative name:** `escalate-over-improvise`. Skill author may rename — `recognize-the-hack`, `production-shaped-solutions`, `no-workarounds`, whatever lands best. Keep the name evocative of the discipline, not the technology.

## Core thesis

Agents are trained toward local optimization: *the work item said make this test pass; the test passes; deliverable met.* When the real environment pushes back (missing native DLL, platform quirk, coverage gate on untestable code), the locally-optimal move is whatever unblocks the task fastest. The globally-optimal move is often to STOP and tell the orchestrator what's weird.

This skill should teach agents to notice the moment they're about to commit a solution they'd be embarrassed to defend in a PR review — and to treat BLOCKED as a first-class outcome, not a failure.

## When to apply

Always, but especially during:

- Integration work with platform dependencies (native libraries, OS APIs, hardware)
- Test-writing where the production path is underspecified
- Coverage-gated work where unreachable branches and platform-bound classes show up
- Phases that depend on environment state (caches, emulators, toolchain versions)

## Red-flag patterns — escalate, do not ship

Concrete triggers. If the agent's draft solution contains any of these, STOP.

1. **Reading binaries or assets from an unrelated application's install directory.** Example: copying FFmpeg DLLs from `$(ProgramFiles)\obs-studio\bin\64bit\`. The dependency chain is real and the app happens to ship it — that doesn't make it a supported acquisition path.
2. **`[ExcludeFromCodeCoverage]` or equivalent on production code that throws / stubs.** Example: `CliServices.CreateDefault()` annotated with `[ExcludeFromCodeCoverage]` and throwing `PlatformNotSupportedException`. That's hiding an unimplemented production path behind a coverage exclusion. Integration tests will lie about what's working.
3. **Production-shaped code placed in a test project.** Example: real TCP/UDP adapters living under `tests/...Integration.Tests/` because "the test needs them and the spec didn't say where production wiring goes." If it looks like production code, escalate — the orchestrator will tell you where it belongs.
4. **Hard-coded workarounds for specific OS/emulator versions.** Example: forcing a specific MediaCodec codec name to avoid a broken async callback on `c2.goldfish.h264.decoder`. If the fix is hard-coded without an injection seam, real hardware will break. A test seam with a default → good. A hard-coded emulator-only branch in production → escalate.
5. **Copying files between concurrent worktrees.** Example: pulling `local.properties` from a sibling agent's worktree. That's cross-contamination. If you need file X and don't have it, the orchestrator failed to provide it — say so.
6. **Silent fallbacks.** Example: `git worktree add ... 2>/dev/null || true` swallowing a creation failure. If the operation fails, fail loud; don't let the caller believe success.
7. **Lowering a threshold to escape a gate.** Example: GOP=2 instead of fixing the consumer that can't drain the NVENC queue. Changing the test to match the bug is not a fix.
8. **Parameterizing a solution that should be a single choice.** Example: adding a `codecName: String? = null` parameter "to allow tests to pick a different codec" when only one production codec name is correct. Sometimes the right shape; sometimes an escape hatch. Distinguish by asking: does the parameter have a legitimate production use-case with a non-null value? If no, it's a test seam masquerading as an injection point — document that clearly or escalate.
9. **Adding a dependency that was previously not needed, without an obvious reason.** Example: agent pulls in `mockk` mid-phase when `mockk` wasn't previously referenced by the task. New deps → escalate.
10. **TODO / FIXME / "temporary" left in committed code.** Rationale later becomes rationale never.

Not every "difficult" solution is a hack. Factory-parameter injection, injectable clocks, extracted pure-logic helpers — these are good design. The distinction: does the shape of the code make the problem easier to reason about, or is it a dodge so the current task passes?

Ask: *"If a senior engineer saw this PR and it touched X, would I be comfortable defending it?"* If the answer involves words like "well, it's just for the test" or "this machine happens to have", that's the signal.

## Escalation format

When STOP is triggered, the agent emits `BLOCKED` with:

- **What task you're blocked on** (task number, phase)
- **What you were about to commit** (concrete: file paths, behavior summary)
- **Why it felt wrong** (which red flag above; what specifically is the smell)
- **What you tried** (alternatives you considered)
- **What you'd need to proceed cleanly** (orchestrator-side prep: pre-placed DLLs, an injection point agreed upon, a spec clarification)

Do NOT commit the hack "as a starting point." The orchestrator handles it. BLOCKED is a complete outcome.

## What the orchestrator does with BLOCKED

(Context for agents; not their concern.) The orchestrator either:

- Fixes the upstream gap and re-dispatches (e.g., pre-places FFmpeg DLLs, updates the spec)
- Narrows the task scope and re-dispatches
- Accepts the hack with explicit acknowledgment ("ok, ship the OBS copy for now, I'll replace with BtbN downloader next round")

The point: the agent doesn't carry the decision alone. Escalation is cheap.

## Structure suggestion

```text
~/skills-dev/escalate-over-improvise/
  SKILL.md                  # thesis, triggers, red flags, escalation format
  references/
    red-flag-patterns.md    # each pattern with a concrete example from real session traces
    injection-vs-escape.md  # distinguishing test seams from escape hatches
    escalation-template.md  # the BLOCKED report format
```

## Session-specific context (for the skill author)

The WindowStream session (April 2026, Windows-to-Android-XR window streaming) surfaced all ten red-flag patterns above. Concrete examples for references:

- **OBS DLL copy**: Phase 12 integration test needed FFmpeg native DLLs; no NuGet runtime package for v7 is available; agent added a conditional `.csproj` copy reaching into `$(ProgramFiles)\obs-studio\bin\64bit\`. Should have been BLOCKED → orchestrator adds a BtbN-builds downloader.
- **CliServices PlatformNotSupportedException + ExcludeFromCodeCoverage**: Phase 11 CLI agent couldn't figure out how to wire real production services from a cross-platform test, so stubbed `CreateDefault()` with a throw and excluded it from coverage. Silent impact: the CLI literally doesn't work end-to-end in production, but tests pass.
- **Adapters in test project**: Phase 12 agent built `TcpConnectionAcceptorAdapter` etc. under `tests/WindowStream.Integration.Tests/` because no one told it where production wiring belongs. Integration test works; production composition is still a gap.
- **Hard-coded emulator codec**: Phase 13 agent passed `codecName = "c2.android.avc.decoder"` to dodge a broken goldfish codec. In this case the agent DID use the right shape (default = null, test overrides) — a counterexample showing what GOOD looks like.
- **`|| true` in worktree hook**: user's `worktree-from-head.sh` swallowed `git worktree add` failures; caused multiple agents to work on main when parallel creation raced. Loud-failure fix restored isolation.
- **GOP=2 NVENC workaround**: agent dropped GOP length to avoid filling the encoder queue instead of fixing the consumer drain rate. Documented as a test-only setting; should have been escalated as a protocol/design question.

Reference these in the skill with short excerpts from the actual commits / reports.

## Deployment

Follow the user's standard skill deployment: develop in `~/skills-dev/`, install to `~/.claude/skills/`, publish to GitHub if appropriate (per `reference_skills_dev.md`).
