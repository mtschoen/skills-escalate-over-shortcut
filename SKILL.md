---
name: escalate-over-shortcut
description: "Use when about to commit a draft solution that suppresses a problem (silent fallbacks like || true, [ExcludeFromCodeCoverage] on throw/stub code, lowered thresholds), pulls state from somewhere illegitimate (binaries from an unrelated app's install dir, prod wiring under tests/, cross-worktree file copies), adds configurability with no production caller (hard-coded values keyed to one platform, test-only knobs), or leaves rationale-free drift (mid-phase dependencies, TODO/FIXME, unexplained changes). Emit BLOCKED to the orchestrator (or user) instead of shipping the shortcut. Claude→self companion to pushback; fires on the agent's own draft, not on the user's request. Most invocations end \"no, not a shortcut, ship\" — that's healthy; the value is the check."
---

# Escalate Over Shortcut

## Why this skill exists

Agents optimize locally. The work item said "make this phase pass"; the phase passes; deliverable met. When the real environment pushes back — a missing native DLL, a platform-bound class, a coverage gate over untestable code, a flaky emulator — the locally-optimal move is whatever unblocks the task fastest. The globally-optimal move is often to **STOP** and tell the orchestrator what's weird.

**The failure mode this skill prevents:** the agent silently ships a shortcut, the build looks green, the integration is actually broken. Escalation is cheap; the agent isn't the right one to absorb that decision alone.

**The failure mode this skill must NOT create:** a paranoid agent that flags every careful piece of design as a shortcut. The bar is *concrete*: the draft contains a pattern the agent would be embarrassed to defend in PR review.

This is **agent → self** review. Companion to `pushback`, which is Claude → user.

## When this fires

You're holding a draft solution and one of these shapes is present. Each is a class of smell; full catalogue with code excerpts is in `references/red-flag-patterns.md`.

- **Suppressing a problem instead of fixing it.** Silent fallbacks (`|| true`, empty `catch`), coverage exclusions on stub/throw code, lowered thresholds to escape a gate. The problem becomes invisible; the gate goes green; the integration is still broken.
- **Pulling state from somewhere illegitimate.** Reading binaries from an unrelated app's install dir, copying files between concurrent worktrees, placing production-shaped wiring under `tests/`. The diff works locally because *this* environment happens to provide what's needed; it won't elsewhere.
- **Configurability that only tests use.** Hard-coded values keyed to one platform, parameters with no production caller, "test-only" knobs. Sometimes the right shape — see the next section.
- **Unexplained mid-task drift.** A dependency added mid-phase with no brief support, TODO/FIXME left in code, "temporary" constants. The rationale is in your head right now; it won't be in PR review.
- **Placeholder-as-answer.** A no-op return (`return []`, `return None`, an empty handler body) shipped instead of the real implementation, with reasoning like *"the honest state when X isn't wired yet"* or *"the test's assertions hold vacuously over an empty collection."* The test passes — but only because there's nothing to assert against, not because the work was done. The tell: you're defending the placeholder as *"not the obvious shortcut, since I didn't fake the data."* Avoiding the obvious shortcut isn't the same as doing the work; the missing wiring is the actual problem and the empty return makes it invisible. Right move: BLOCKED, name the missing wiring, ask whether to fake (with explicit acceptance) or stop.

If your draft contains *something that rhymes with these but isn't on the list* — the gut check catches it.

## The gut check

> *"If a senior engineer saw this PR and it touched X, would I be comfortable defending it?"*

If the defense involves "well, it's just for the test" or "this machine happens to have it" or "we can fix this in the next round" — **that's the signal**. STOP and escalate.

The check applies even when no pattern above matches verbatim. The shapes are the *common forms* of the failure; the gut check is the underlying discipline.

## Test seam vs. escape hatch

Adding configurability is not, by itself, a shortcut. The distinguishing question is **not** "does the default have a non-null value" — every parameter has *some* default. The question is about call sites:

> **Does any production call site pass a value other than the default?**

Equivalent gut-check: *if you deleted the parameter and inlined the default as a constant, would any production code break?*

- **Yes, real production callers pass non-default values** → injection seam. A `Clock` parameter that defaults to `Clock.systemUTC()` and is wired with a timezone-aware clock from the composition root is real configurability.
- **No, every production caller uses the default; only the test passes something else** → escape hatch. The parameter exists *solely* so the test can override it. That's a test-only knob dressed up as a constructor param. Escalate to ask whether the production code should be re-shaped instead — use the test framework's virtual time (`runTest` + `advanceTimeBy`), expose a `Scheduler` the production composition actually wires, or inject a real abstraction with a meaningful production value.

When in doubt — escalate.

## The BLOCKED escalation

When STOP triggers, emit `BLOCKED` with five fields. This is a complete outcome — not a "starting point" — and the orchestrator handles it.

```text
## BLOCKED

**Task:** Phase 12, task 3 — wire FFmpeg native DLLs for integration test
**About to commit:** `WindowStream.Integration.Tests.csproj` step that copies
  ffmpeg-*.dll out of `$(ProgramFiles)\obs-studio\bin\64bit\` into the
  test output directory.
**Smell:** reading binaries from an unrelated app's install dir. OBS happens
  to ship FFmpeg 7 DLLs; that's not a supported acquisition path.
**Tried:**
  - NuGet: no `FFmpeg.AutoGen.runtime.*` for v7 published.
  - Manual download: BtbN release builds available, no automation in place.
  - vcpkg: not configured in this repo.
**To proceed cleanly:** orchestrator pre-places `ffmpeg-*.dll` (e.g.,
  via a small downloader invoked by the build), or accepts the OBS copy
  explicitly as a knowingly-fragile starting point.
```

1. **Task** — phase + task number + brief context.
2. **About to commit** — the actual diff: file paths and one-line behaviour.
3. **Smell** — which shape, and *why specifically* it's wrong-shaped.
4. **Tried** — alternatives considered and what blocked each. Shows the search space.
5. **To proceed cleanly** — what the orchestrator would need to provide.

Do **not** ship the shortcut alongside the BLOCKED. The orchestrator's decision (accept the shortcut, fix the upstream gap, narrow scope) is clean only if the diff doesn't exist yet.

## When the user is the orchestrator

In a foreground session, the user IS the orchestrator. Same five fields, inline:

> "Heads up before I commit X — looks like a [smell]. Tried A, B, C; each blocked by [reason]. Cleanest path forward is [orchestrator action]; otherwise [the shortcut] as known-fragile. Which?"

One line back from the user resolves it. The point is awareness *before* the shortcut lands, not litigation of the design.

## What this is NOT

**Not pushback.** Pushback is Claude → user, fired on the *user's* requests. This is Claude → self, fired on the *agent's* drafts. If the user asks for something that looks like a shortcut, that's pushback. If you're about to commit something on your own initiative that looks like a shortcut, that's this skill.

**Not smoke-test.** Smoke-test asks "does the change work?" This skill asks "is the change shaped right?" A smoke-pass on a shortcut-shaped solution is the exact failure mode this skill prevents — the test passes, the integration is broken.

**Not pessimism.** Most drafts ship cleanly. Most invocations end in *"no, not a shortcut, ship."* That's healthy; the value is the check.

**Not paranoia about test code.** Mocks, fakes, injectable parameters with sensible defaults — these are good design. The test-seam-vs-escape-hatch question above tells you which is which.

## Self-check before shipping

Before any "phase done" or commit, silently answer:

- Does the diff contain a pattern from the shapes above, or something rhyming?
- Would I defend the shape of this change to a senior engineer without "just for the test" or "this machine happens to have"?
- If a parameter or knob is new, does any production call site pass a non-default value? (If every production caller uses the default and only the test overrides it, it's a test-only knob — escalate.)
- If I added a dependency, did the brief ask for it?
- If something is suppressing a failure (`|| true`, empty `catch`, `[ExcludeFromCodeCoverage]`), is the suppression itself the thing I should escalate?
- If the answer I'm about to ship is empty / zero / no-op (`return []`, `return None`, empty body): does the test pass *because the work was done*, or *because there's nothing for the assertions to fail against*? If the latter, the work isn't done — escalate the missing wiring.

If any check trips: **STOP, emit BLOCKED, do not commit the diff.** The orchestrator handles it.

If all checks pass: ship.
