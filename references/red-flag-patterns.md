# Red-Flag Patterns — Full Catalogue

`SKILL.md` collapses these into four shape clusters. This file is the long-form catalogue: each pattern with the concrete code excerpt from the real session that surfaced it. Use SKILL.md for the discipline; come here when you need to see whether a specific draft matches a known shape.

All examples are drawn from the WindowStream session (April 2026) — a Windows → Android-XR window-streaming build that ran several phases of parallel subagent work and surfaced every pattern below. Where possible the excerpt is the actual diff that triggered the lesson.

## Index

- **Suppressing a problem instead of fixing it**
  - [Silent fallbacks](#silent-fallbacks)
  - [Coverage exclusions on stub/throw code](#coverage-exclusions-on-stubthrow-code)
  - [Lowering a threshold to escape a gate](#lowering-a-threshold-to-escape-a-gate)
- **Pulling state from somewhere illegitimate**
  - [Reading from an unrelated app's install dir](#reading-from-an-unrelated-apps-install-dir)
  - [Production-shaped code under `tests/`](#production-shaped-code-under-tests)
  - [Copying files between concurrent worktrees](#copying-files-between-concurrent-worktrees)
- **Configurability that only tests use**
  - [Hard-coded values keyed to one platform](#hard-coded-values-keyed-to-one-platform)
  - [Parameters with no production caller](#parameters-with-no-production-caller)
- **Unexplained mid-task drift**
  - [Mid-phase dependency additions](#mid-phase-dependency-additions)
  - [TODO / FIXME / "temporary" in committed code](#todo--fixme--temporary-in-committed-code)
- **Cross-cutting**
  - [What GOOD looks like — the codec-name counterexample](#what-good-looks-like--the-codec-name-counterexample)
  - [Test seam vs. escape hatch — the longer answer](#test-seam-vs-escape-hatch--the-longer-answer)

---

## Suppressing a problem instead of fixing it

### Silent fallbacks

A failure mode is swallowed so the caller can't see it. The caller proceeds as if the operation succeeded; later breakage is hard to attribute.

**Real example.** `worktree-from-head.sh` contained:

```bash
git worktree add "$wt_dir" "$branch" 2>/dev/null || true
```

When `git worktree add` failed (branch already checked out elsewhere, dirty index, name collision), the script claimed success. Multiple parallel agents then operated on `main` instead of their own worktree, racing on the same files.

**Loud-failure fix.** Drop the `|| true` and the `2>/dev/null`. Surface the error; let the orchestrator route around it.

**Generalised shape.** Any `2>/dev/null`, any `|| true`, any empty `catch (Exception _)` on an operation whose failure is meaningful. If the operation can fail and you don't want it to halt, the right move is *explicit handling* (check `$?`, branch on the exception type) — not invisibility.

### Coverage exclusions on stub/throw code

`[ExcludeFromCodeCoverage]` (or the equivalent attribute in your language) applied to production code that isn't actually implemented. The coverage report stays green; the production path doesn't exist.

**Real example.** Phase 11 CLI work couldn't figure out how to wire real production services from a cross-platform test, so the agent shipped:

```csharp
[ExcludeFromCodeCoverage]
public static ICliServices CreateDefault()
{
    throw new PlatformNotSupportedException(
        "CliServices.CreateDefault is not yet wired for this platform.");
}
```

The integration tests passed. The CLI literally didn't work end-to-end in production.

**The smell isn't the attribute — it's combining it with a throw/stub.** Excluding genuinely platform-bound code (a Win32 P/Invoke wrapper, an Android Binder helper) from line coverage is reasonable when there's a real test for the supported platform. Excluding a `throw new PlatformNotSupportedException()` masks the gap.

**Right move.** Escalate: the CLI needs a production wiring point and the agent doesn't have the spec for what it should be.

### Lowering a threshold to escape a gate

A test fails because the production code can't keep up. The agent tunes the test's threshold instead of fixing the production code.

**Real example.** An NVENC encoder integration test failed because the consumer wasn't draining the encoder's output queue fast enough; the encoder backed up and dropped frames. The agent dropped GOP length from a realistic value to `GOP=2`, which shrank the queue depth enough that the test passed — but the underlying drain-rate bug was untouched.

**The cue.** When you change a test's threshold, ask: *did the production code's behaviour change for the better, or did I just stop the test from noticing the existing behaviour?* If the latter — escalate. The test was right.

**Adjacent shape.** Bumping a flaky test's retry count. Lowering a flake-rate threshold. Disabling a CI check "just for this PR." All variants of the same move.

---

## Pulling state from somewhere illegitimate

### Reading from an unrelated app's install dir

The build needs an asset (a DLL, a font, a data file). No supported acquisition path exists. The agent finds the asset *on this machine* in some unrelated application's install directory and reaches in.

**Real example.** Phase 12 integration tests needed FFmpeg native DLLs (v7). No NuGet runtime package for FFmpeg 7 was published. The agent added to `WindowStream.Integration.Tests.csproj`:

```xml
<Target Name="CopyFFmpegFromOBS" BeforeTargets="Build">
  <ItemGroup>
    <FFmpegDlls Include="$(ProgramFiles)\obs-studio\bin\64bit\*.dll" />
  </ItemGroup>
  <Copy SourceFiles="@(FFmpegDlls)" DestinationFolder="$(OutDir)" />
</Target>
```

The integration test then ran. The build was *de facto* dependent on a user-installed copy of OBS Studio.

**Right move.** BLOCKED. The orchestrator either (a) adds a real acquisition path — a downloader script invoking BtbN release builds — or (b) explicitly accepts the OBS dependency as known-fragile while waiting for the real fix.

**Generalised shape.** Any reach into an install-dir, registry hive, package-manager cache, or sibling user's `~/Downloads/` to acquire a build input. The dependency chain becomes invisible the moment that other software is uninstalled or upgraded.

### Production-shaped code under `tests/`

Real production wiring (network adapters, service implementations, dependency-injection composition) placed inside a test project because "the test needs it and the spec didn't say where the production version goes."

**Real example.** Phase 12 needed `TcpConnectionAcceptorAdapter` and `UdpConnectionAdapter` — real network code — to drive the integration test. The agent put them under `tests/WindowStream.Integration.Tests/Adapters/`. Integration tests passed; the production composition still had no network wiring at all.

**The cue.** Look at the *shape* of the code you're about to commit:

- A fake/mock/stub that exists for tests → belongs in `tests/`.
- Real production behaviour → belongs in production, even if tests are currently the only caller.

**Right move.** BLOCKED. The orchestrator says where the adapters belong in the production tree.

### Copying files between concurrent worktrees

In a multi-agent fan-out where each agent has its own worktree, one agent needs a file that lives in another agent's worktree (or branch). Instead of asking the orchestrator to provide it, the agent reaches sideways.

**Real example.** A subagent needed `local.properties` (Android SDK path) which a sibling agent had set up. The first agent copied it directly from `../sibling-worktree/local.properties` into its own worktree.

**Why it's wrong.** Worktrees exist *because* parallel work needs isolation. Cross-worktree reads break that guarantee silently; the next time a sibling worktree is missing or differently-configured, the reading agent fails for non-obvious reasons.

**Right move.** BLOCKED. The orchestrator either pre-places the file in every worktree, captures it as a shared resource (e.g., a sibling sentinel committed to the repo), or explicitly provides it in the agent's brief.

---

## Configurability that only tests use

### Hard-coded values keyed to one platform

The agent encounters a platform-specific bug (a broken codec, a quirky kernel call, a deprecated API). Instead of finding a portable solution or escalating, the agent hard-codes the working value into production.

**Real example.** Phase 13 work hit a broken `c2.goldfish.h264.decoder` on the Android emulator. A different codec, `c2.android.avc.decoder`, worked. The agent hard-coded `codecName = "c2.android.avc.decoder"` directly into the production MediaCodec construction call.

On real hardware this would break — the working codec is platform-specific. On the emulator it papered over the bug.

**Right move.** Either pass a default that the system picks (`null` → MediaCodec selects an appropriate codec for the device) with the test overriding for the emulator, OR escalate as a protocol/design question. See [What GOOD looks like](#what-good-looks-like--the-codec-name-counterexample) below — Phase 13 actually got this right in a second pass.

### Parameters with no production caller

The agent adds a parameter to a production function "so tests can override it" — but no production code path supplies a non-default value.

**Why it's a smell.** It pollutes the production signature for a test-only need; future readers can't tell which parameters are real configurability and which are test escape hatches.

**Distinguishing question.**

> Does any production call site pass a value other than the default?

Equivalent gut-check: *if you deleted the parameter and inlined the default as a constant, would any production code break?*

If yes — real production callers pass non-default values — it's an injection seam. Real configurability.
If no — every production caller uses the default and only the test overrides it — it's an escape hatch. Document the test-only intent in a comment, or (better) escalate to ask whether the production code should be re-shaped instead.

See [Test seam vs. escape hatch — the longer answer](#test-seam-vs-escape-hatch--the-longer-answer) below for the full treatment.

---

## Unexplained mid-task drift

### Mid-phase dependency additions

A new third-party dependency appears mid-task, not requested by the brief.

**Real example.** A subagent pulled `mockk` (a Kotlin mocking library) into a project that hadn't referenced it before. The task brief didn't ask for mocks; the agent decided the easier path was to mock a collaborator rather than wire the real one.

**Why escalate.** New deps have licence, security, build-time, and review-burden costs that the orchestrator should price. They also frequently signal that the agent took a different shape than the brief intended — the mock substitutes for a real wiring decision the orchestrator may have wanted to make.

**Right move.** BLOCKED. List the dep, the function it's serving, the alternatives considered. The orchestrator decides.

### TODO / FIXME / "temporary" in committed code

The agent leaves a marker for future work in code it's about to commit.

**Why escalate.** "I'll come back to this" is rarely true. The marker becomes a permanent confession in the codebase, then a permanent silence when no one comes back. If the work isn't done, the right outcome is BLOCKED — not a marker.

**Right move.** Either finish the work, or escalate the gap with a BLOCKED. Don't commit the marker.

**Narrow exception.** A TODO that references a *tracked* issue (e.g., `// TODO(#1234): replace with downloader once available`) is a different thing — it's a pointer to scheduled work, not a confession. But this is also work the orchestrator should have created the issue for; check before committing.

---

## What GOOD looks like — the codec-name counterexample

After the first Phase 13 attempt hard-coded `codecName = "c2.android.avc.decoder"`, the next pass got it right. The shape they ended up with:

```kotlin
class VideoDecoder(
    private val codecName: String? = null,  // null → MediaCodec picks
    // ... other params
) {
    private val codec = if (codecName != null) {
        MediaCodec.createByCodecName(codecName)
    } else {
        MediaCodec.createDecoderByType(MimeTypes.AVC)
    }
}
```

Three things that make this an injection seam rather than an escape hatch:

1. **Default has a real production behaviour.** `null` → "let the system pick the appropriate decoder for this device." That's the production answer, not "this only works in tests."
2. **The override path is the test path.** Tests that need to dodge a specific broken codec pass `codecName = "c2.android.avc.decoder"` explicitly. Production callers leave it null.
3. **The signature documents itself.** A reader sees `codecName: String? = null` and immediately understands: "the system normally chooses; callers can override." No "test-only" comment needed.

Contrast with the bad shape, which was simply `codecName = "c2.android.avc.decoder"` written into the production construction call — no parameter, no seam, just a hard-coded value that worked on the one machine the agent tested on.

**The shape of the diff is the difference between escalation-worthy and ship-worthy.** Same underlying compatibility problem; entirely different code.

---

## Test seam vs. escape hatch — the longer answer

The distinguishing question (`Does any production call site pass a value other than the default?`) handles the obvious cases. The harder cases:

### The default is currently null but might not be forever

A new feature ships with one production strategy and a parameter that *could* support alternates. Today only tests use the override. Tomorrow, a second production caller might use a non-null value.

**Treatment.** This is a seam if you have a concrete plan for a future non-null caller — a tracked feature, a known upcoming integration, a documented extensibility point. It's an escape hatch if "tomorrow" is hand-waving.

When you can't tell, the BLOCKED is short: "Adding `strategy: Strategy? = null` to support test overrides. Production only uses the default today. Is this a seam (planned future caller?) or should I find a different way?"

### The override is "needed" only because a real production bug exists

You're tempted to add a parameter so the test can supply a value that dodges a bug in the default code path. That's not configurability — it's a feature flag for "skip the broken thing." The right escalation isn't "should this be a seam"; it's "the default behaviour is wrong, here's what I observed."

**Treatment.** BLOCKED on the underlying behaviour. Don't paper over with a knob.

### The override is for performance, not correctness

Tests use a fast cheap version; production uses a slow expensive one. This *is* a real seam — the production caller has a non-null value (the slow path), the test caller has a non-null value (the fast path). Document the trade-off (typically in the function's docstring), and ship.

### The override is for determinism, not correctness

Tests inject a fixed clock, a seeded random, a stable timestamp. Production injects the real clock, the real random, the real wall-time. Same story as performance: real seam, both sides have non-null callers.

---

## How to use this catalogue

When you suspect your draft has a problem:

1. Run the SKILL.md gut check first — *would I defend this to a senior engineer without "just for the test" or "this machine happens to have"?*
2. If the gut check trips, find the closest matching shape above and read the section. Some patterns look superficially fine (e.g., a hard-coded codec name) until you see the diff that triggered the lesson.
3. If your draft genuinely doesn't match any pattern here — that's a useful signal in itself. The shapes here are *common*. A draft that doesn't match any of them and still feels wrong may be a new shape worth naming; escalate with the gut-check observation as the smell.
