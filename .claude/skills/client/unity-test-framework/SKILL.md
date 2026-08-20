---
name: unity-test-framework
description: >
  Technique for Unity's Test Framework package (`com.unity.test-framework`,
  namespaces `UnityEngine.TestTools`, `UnityEditor.TestTools`,
  `UnityEditor.TestTools.TestRunner.Api`, `UnityEngine.TestRunner`) — a
  customized NUnit 3.5 integration for **Edit Mode** and **Play Mode**
  automated tests, run through the **Test Runner window**
  (`Window > General > Test Runner`) or the command line. Covers creating
  Test Assemblies (`.asmdef` referencing `nunit.framework.dll`,
  `UnityEngine.TestRunner`, and Edit-Mode-only `UnityEditor.TestRunner`) and
  test scripts; the Edit Mode vs. Play Mode distinction and the 2.0
  `RequiresPlayModeAttribute` mechanism that lets both live in one assembly;
  Unity's custom attributes on top of plain NUnit (`UnityTestAttribute` for
  coroutine-style tests, `UnitySetUpAttribute`/`UnityTearDownAttribute`,
  `ConditionalIgnoreAttribute`, `ParameterizedIgnoreAttribute`,
  `PrebuildSetupAttribute`/`PostBuildCleanupAttribute` with
  `IPrebuildSetup`/`IPostBuildCleanup`, `UnityPlatformAttribute`,
  `RequirePlatformSupportAttribute`, `TestPlayerBuildModifierAttribute` with
  `ITestPlayerBuildModifier`, `TestMustExpectAllLogsAttribute`,
  `PreservedValuesAttribute`, `TestRunCallbackAttribute`); the full outer-
  action execution order (`IApplyToContext` → `IOuterUnityTestAction.BeforeTest`
  → `UnitySetUp` → NUnit `SetUp` → test → NUnit `TearDown` →
  `UnityTearDown` → `IOuterUnityTestAction.AfterTest`) and its domain-reload
  survival rules; parameterized tests (`TestCase`/`ValueSource`, with
  `UnityTest` supporting only `ValueSource`) and 2.0's async `Task`-based
  tests; custom Edit Mode yield instructions (`EnterPlayMode`, `ExitPlayMode`,
  `RecompileScripts`, `WaitForDomainReload`, `IEditModeTestYieldInstruction`);
  `LogAssert.Expect`/`NoUnexpectedReceived` for expecting Unity log messages,
  the `Utils` equality comparers (`Color`/`Float`/`Quaternion`/`Vector2`/
  `Vector3`/`Vector4`) and custom `Constraints`; `IMonoBehaviourTest`/
  `MonoBehaviourTest<T>` for coroutine-driven MonoBehaviour tests; running
  Play Mode tests in a standalone Player (`Run Location: On Player`) and the
  full `-runTests`/`-batchmode`/`-testFilter`/`-testCategory`/`-testPlatform`/
  `-testResults`/`-assemblyNames`/`-testSettingsFile` command-line surface for
  CI; and the programmatic `TestRunnerApi` (`Filter`, `ExecutionSettings`,
  `ICallbacks`/`IErrorCallbacks` vs. the Player-capable
  `UnityEngine.TestRunner.ITestRunCallback`/`TestRunCallbackAttribute` pair).
  Use this for writing/running Edit Mode unit tests against `Game.Core.*`
  Shared Core logic, Play Mode integration tests exercising
  `Game.Client.*`/MonoBehaviour behavior, and network-condition test cases
  when the backend track is active — the qa-automation-engineer's primary
  toolkit, invoked after code has already passed Code Review. Do not use
  this for the actual game-rule logic under test (damage formulas, state
  machines, economy math) — that belongs in `Game.Core.*` per
  `coding-principles.md`'s Shared Core integrity rule; this skill only
  verifies it. Do not use this for manual Play Mode walkthroughs comparing
  behavior against the GDD with screenshots — that's `playtest-tester`'s
  territory, a different activity from this skill's automated, assertion-
  based tests even though both can run inside Play Mode. Do not use this for
  producing a real platform build or running multiple simultaneous Editor
  instances — per this project's team structure only `build-run-engineer`
  does that, and only when the GD explicitly asks; this skill's standalone-
  Player and command-line coverage is reference material for that role, not
  routine QA workflow. Do not use this for profiling/measuring performance
  (frame time, GC allocations via the Profiler) — that's
  `unity-profiler-diagnostics`/`tech-lead-performance`'s territory; this
  skill's `Constraints`-based allocation assertions are a correctness gate,
  not a profiling tool. Do not use this to relitigate general NUnit/TDD
  fundamentals (plain `Test`/`TestCase`/`SetUp`/`TearDown`/`Assert.*`) that
  aren't Unity-specific — this skill only covers Unity's additions on top;
  point to NUnit's own documentation for the rest.
---

# Unity Test Framework — Edit Mode & Play Mode Testing

Sources: see [references/](references/) for the specific sub-pages this skill was built from, split by topic — [root-links.md](references/root-links.md), [getting-started-and-workflows.md](references/getting-started-and-workflows.md) (overview, requirements, known limitations, Edit Mode vs. Play Mode, creating tests/assemblies, running tests, what's new in 2.0), [attributes-reference.md](references/attributes-reference.md) (the full custom-attribute catalog), [execution-order-and-setup-cleanup.md](references/execution-order-and-setup-cleanup.md) (`IPrebuildSetup`/`IPostBuildCleanup`, `IOuterUnityTestAction`, the 12-step action order, domain-reload rules), [async-coroutine-and-parameterized-tests.md](references/async-coroutine-and-parameterized-tests.md) (`UnityTest`, async `Task` tests, `TestCase`/`ValueSource`, custom yield instructions), [assertions-logging-and-monobehaviour-testing.md](references/assertions-logging-and-monobehaviour-testing.md) (`LogAssert`, equality comparers, `Constraints`, `MonoBehaviourTest<T>`, `ConditionalIgnore`), [platform-build-and-command-line.md](references/platform-build-and-command-line.md) (platform/build attributes, standalone Player runs, full CLI reference), [scripting-api-test-runner-api.md](references/scripting-api-test-runner-api.md) (`TestRunnerApi`, `Filter`, `ExecutionSettings`, both callback interfaces).

## 1. Objective

Write and run correct, deterministic Edit Mode and Play Mode tests against already-Code-Reviewed client-track code — the right test assembly/attribute/execution-order setup, the right way to express a multi-frame or asynchronous assertion, and the right log/allocation/platform expectation — without duplicating game-rule logic into the test layer, without drifting into manual playtesting or platform-build territory that belong to sibling roles, and without silently accepting a flaky or non-deterministic test as "passing."

## 2. Role

Act as the automated-testing specialist for the client track: given code that has already passed Code Review, choose the right UTF constructs to verify it — Edit Mode unit tests for `Game.Core.*` Shared Core logic, Play Mode integration tests for `Game.Client.*` MonoBehaviour/scene behavior, and (when the backend track is active) network-condition test cases. This skill does not decide what the *game rules* are (that's `csharp-engineer`'s Shared Core), does not manually walk through Play Mode comparing feel against the GDD (that's `playtest-tester`), and does not build/run on real platforms or multiple Editor instances (that's `build-run-engineer`, only on explicit GD request).

## 3. When to invoke this skill

- Setting up a new **Test Assembly** (`.asmdef`) or **test script**, and deciding whether it targets Edit Mode, Play Mode, or both via `[RequiresPlayMode]`.
- Writing an Edit Mode unit test (`[Test]`) against `Game.Core.*` logic — the natural home for verifying deterministic gameplay-rule correctness, since Shared Core has no `UnityEngine` dependency and needs no Play Mode at all.
- Writing a Play Mode integration test (`[UnityTest]`, coroutine-based) exercising a MonoBehaviour, a scene, physics, or multi-frame timing behavior.
- Needing a test to span multiple frames, wait on a coroutine/async operation, or enter/exit Play Mode mid-test (`EnterPlayMode`/`ExitPlayMode`, `[UnitySetUp]`/`[UnityTearDown]`).
- Writing an async `Task`-based test (2.0+) for code that's itself `async`/`await`-based.
- Parameterizing a test (`[TestCase]`/`[TestCaseSource]`/`[ValueSource]`), remembering `[UnityTest]` only supports `[ValueSource]`.
- Asserting on a `Debug.LogError`/`Debug.LogWarning`/`Debug.LogException` the code under test is expected to emit (`LogAssert.Expect`), or that it must not emit anything unexpected (`LogAssert.NoUnexpectedReceived`/`[TestMustExpectAllLogs]`).
- Needing a pre-build data setup or post-build cleanup step tied to specific tests (`IPrebuildSetup`/`IPostBuildCleanup`, `[PrebuildSetup]`/`[PostBuildCleanup]`).
- Conditionally skipping a test based on a runtime condition (`[ConditionalIgnore]`) or specific parameterized arguments (`[ParameterizedIgnore]`), rather than platform (`[UnityPlatform]`/`[RequirePlatformSupport]`).
- Setting up CI to run tests headlessly (`-runTests -batchmode -testFilter/-testCategory/-testPlatform -testResults`) and parse the resulting NUnit-XML report.
- Writing or reviewing custom Editor tooling that drives tests programmatically via `TestRunnerApi` (`Filter`, `ExecutionSettings`, `ICallbacks`/`IErrorCallbacks`) or subscribes to raw test-progress via `[TestRunCallback]`/`ITestRunCallback`.
- Writing a test for a MonoBehaviour whose completion is naturally "run until a condition holds" (`IMonoBehaviourTest`/`MonoBehaviourTest<T>`).
- A network-condition test case (packet loss, latency) once the backend/multiplayer track is active — same UTF mechanics, applied to netcode-adjacent code.
- Negative trigger: deciding or implementing the actual game-rule logic being tested — that's `csharp-engineer`'s `Game.Core.*` (Shared Core integrity rule in `coding-principles.md`).
- Negative trigger: manually walking Play Mode against the GDD with screenshots/console capture — `playtest-tester`'s activity, not an automated assertion-based test.
- Negative trigger: producing a real platform build, or running multiple simultaneous Editor instances — `build-run-engineer`'s territory, only on explicit GD request.
- Negative trigger: profiling frame time/GC allocations with the Unity Profiler — `unity-profiler-diagnostics`/`tech-lead-performance`; this skill's `Constraints` allocation assertions are a pass/fail gate, not a profiling session.
- Negative trigger: general NUnit/TDD fundamentals not specific to Unity's additions — defer to NUnit's own docs.

## 4. How to use this skill

1. **Confirm the code under test already passed Code Review** before writing tests against it, per the `qa-automation-engineer` role's input contract — this skill's tests are a verification gate on reviewed code, not a substitute for review.
2. **Put deterministic gameplay-rule tests in Edit Mode against `Game.Core.*` directly**, per [getting-started-and-workflows.md](references/getting-started-and-workflows.md) — Shared Core has no `UnityEngine` dependency, so it needs no Play Mode, no scene, and no MonoBehaviour host to test. Reserve Play Mode (`[UnityTest]`) for behavior that genuinely needs a running scene/frame loop/physics step — MonoBehaviour integration, timing-dependent behavior, prefab instantiation.
3. **Choose the assembly/attribute combination deliberately**, per [getting-started-and-workflows.md](references/getting-started-and-workflows.md): a dedicated Editor-only Test Assembly for pure Edit Mode tests, or a platform-targeted assembly with `[RequiresPlayMode(false)]` on the Edit-Mode-only subset — don't default to physically separate assemblies now that `[RequiresPlayMode]` makes that unnecessary (YAGNI), but don't merge assemblies either if the project already has an established separate-assembly convention predating 2.0.
4. **Because Shared Core must be deterministic** (no `UnityEngine.Random`, no wall-clock time — per `coding-principles.md`'s Shared Core integrity rule), a `Game.Core.*` test should inject a fixed seed/fake clock through the same abstraction production code uses, never rely on real randomness/timing and then assert loosely "close enough" — a flaky Edit Mode test is exactly the signal that Shared Core determinism was violated somewhere, not something to paper over with a wider assertion tolerance.
5. **Reach for `[UnityTest]`/coroutine tests only when the test genuinely needs to span frames** (waiting on physics, an animation, a coroutine, a multi-frame state machine tick). For a single-frame check, a plain `[Test]` is simpler (KISS) — don't wrap a same-frame assertion in an unnecessary `yield return null`.
6. **Get the execution order right before debugging a mysterious setup/teardown interaction** — consult [execution-order-and-setup-cleanup.md](references/execution-order-and-setup-cleanup.md)'s 12-step pipeline and the domain-reload survival rule (`UnitySetUp` does not restart from the top after a domain reload the way plain `SetUp` does) before assuming a bug in the code under test.
7. **Use `LogAssert.Expect` proactively for any log the code under test is intentionally expected to emit**, called *before* the code runs (checks happen at frame end, per [assertions-logging-and-monobehaviour-testing.md](references/assertions-logging-and-monobehaviour-testing.md)) — an un-expected `Debug.LogError` silently fails the test rather than passing by accident.
8. **Validate a "no per-frame allocation" claim about `Game.Client.*` hot-path code with an actual `Constraints`-based allocation assertion** where practical, rather than asserting it from code review alone — this gives `performance-and-algorithms.md`'s no-allocation rule an automated regression gate, not just a one-time manual check.
9. **For CI, always pair `-runTests` with `-batchmode`**, and pick `-testFilter`/`-testCategory`/`-assemblyNames` deliberately to scope a run rather than always running the full suite, per [platform-build-and-command-line.md](references/platform-build-and-command-line.md) — parse `-testResults`' output as standard NUnit XML.
10. **Only reach for `TestRunnerApi`** (per [scripting-api-test-runner-api.md](references/scripting-api-test-runner-api.md)) when building genuine custom Editor tooling around test execution — prefer the Test Runner window and CLI flags for routine runs (KISS); when you do use it, call the **static** methods (`ExecuteTestRun`, `RegisterTestCallback`) since the instance methods are flagged for future obsolescence.
11. **Hand off what's out of scope explicitly**: the game-rule logic itself → `csharp-engineer`. Manual GDD-comparison playtesting → `playtest-tester`. Real platform builds/multi-instance runs → `build-run-engineer`, GD-approved only. Deep performance investigation beyond a pass/fail allocation assertion → `tech-lead-performance`/`unity-profiler-diagnostics`. A failure that keeps recurring after a fix → routes back through Code Reviewer before re-testing, per the `qa-automation-engineer` role's rules — never skip that gate because the fix looks small.

## 5. Specific goals / tasks this skill performs

- Creating and configuring Test Assemblies (`.asmdef`) and test scripts for Edit Mode and/or Play Mode.
- Writing Edit Mode unit tests against `Game.Core.*` Shared Core logic.
- Writing Play Mode integration tests (coroutine-based `[UnityTest]`, or `MonoBehaviourTest<T>`) against `Game.Client.*` behavior.
- Writing async `Task`-based tests for async production code.
- Parameterizing tests correctly (`TestCase`/`TestCaseSource`/`ValueSource`, respecting `UnityTest`'s `ValueSource`-only limitation) and conditionally ignoring specific cases.
- Asserting on expected/unexpected log output (`LogAssert`), custom Vector/Color/Quaternion equality, and (where practical) zero-allocation constraints.
- Building pre-build setup / post-build cleanup steps and getting the multi-attribute execution order right.
- Configuring CI to run tests headlessly via the command line and consume the resulting NUnit-XML report.
- Building or reviewing custom Editor tooling against `TestRunnerApi`.
- Writing network-condition test cases (packet loss, latency) once the backend track is active, using the same UTF mechanics.
- Out of scope: game-rule logic itself (`csharp-engineer`'s Shared Core); manual GDD playtesting (`playtest-tester`); real platform builds/multi-instance runs (`build-run-engineer`, GD-approved only); Profiler-based performance investigation (`unity-profiler-diagnostics`/`tech-lead-performance`); general NUnit/TDD fundamentals not specific to Unity's extensions.

## 6. Output format

```
## Unity Test Framework Work — <feature/module under test>
- Code-under-test Code Review status: confirmed passed (per qa-automation-engineer's input contract)
- Test kind: Edit Mode ([Test]) / Play Mode ([UnityTest], coroutine) / async Task / MonoBehaviourTest<T>
- Assembly setup: <asmdef name, Editor-only vs. platform-targeted, [RequiresPlayMode] usage if any>
- Determinism (if testing Game.Core.*): <seeded RNG/fake clock injection confirmed — no real Random/wall-clock relied on>
- Parameterization: <TestCase/TestCaseSource/ValueSource, or "not needed"> — UnityTest ValueSource-only limitation respected
- Setup/cleanup: <SetUp/TearDown, UnitySetUp/UnityTearDown, IPrebuildSetup/IPostBuildCleanup, or "not needed"> — execution order/domain-reload implications noted if relevant
- Log expectations: <LogAssert.Expect calls, or "not applicable"> — placed before the code under test runs
- Allocation/constraint checks: <Constraints-based assertion, or "not applicable/not yet added">
- CI wiring (if applicable): <command-line flags used, -testResults path, category/filter scoping>
- Hand-off: <game-rule logic → csharp-engineer / manual playtest → playtest-tester / platform build → build-run-engineer / deep perf → tech-lead-performance, as applicable>
- Known limitations: <...>
```

## 7. Examples

**Example 1**
- Input: "Write Edit Mode tests for the new ability-cooldown logic in `Game.Core.Combat.CooldownTracker` that just passed Code Review."
- Output: created an Editor-only Test Assembly (or reused an existing one) referencing `nunit.framework.dll`; wrote plain `[Test]` methods (no Play Mode needed — `CooldownTracker` has no `UnityEngine` dependency) that inject a fake, seeded time source through the same interface production code uses (never `Time.time` directly, keeping the test deterministic exactly as `coding-principles.md`'s Shared Core rule requires); asserted cooldown expiry, refresh, and edge-of-window behavior with plain `Assert.*` calls; no `LogAssert`/setup-cleanup attributes needed for this pure-logic case.
- Hand-off: none — this was a self-contained Edit Mode test against already-reviewed Shared Core logic.

**Example 2**
- Input: "Add a Play Mode test verifying the new enemy prefab's `Rigidbody` responds to physics on spawn."
- Output: wrote a `[UnityTest]` coroutine test in a Play Mode assembly, instantiated the prefab, captured its starting Y position, `yield return new WaitForFixedUpdate()`, then asserted the Y position changed — following the framework's own canonical Rigidbody-physics example; no `MonoBehaviourTest<T>` wrapper needed since the assertion is expressed directly in the coroutine rather than via a self-reporting `IsTestFinished` flag.
- Hand-off: none.

**Example 3**
- Input: "A test needs to enter Play Mode partway through, from an Edit Mode assembly."
- Output: used `[UnitySetUp]` yielding `new EnterPlayMode()` and `[UnityTearDown]` yielding `new ExitPlayMode()`, per [async-coroutine-and-parameterized-tests.md](references/async-coroutine-and-parameterized-tests.md); flagged for the author that `UnitySetUp` does **not** re-run after the domain reload that `EnterPlayMode` triggers (unlike a plain NUnit `SetUp`), so any state the setup method sets *before* the `yield` must not be assumed to still need re-establishing after it — verified against [execution-order-and-setup-cleanup.md](references/execution-order-and-setup-cleanup.md)'s domain-reload rule before shipping the test.

**Example 4**
- Input: "GD wants to know if this feature's tests can run against the actual Android device build as part of QA."
- Output: declined to trigger a build directly — explained that producing a real platform build is `build-run-engineer`'s territory per this project's team structure, and only on the GD's explicit request in the current conversation; documented the "On Player" Test Runner workflow and relevant `-testPlatform`/`-buildPlayerPath`/`-androidAppBundle` command-line flags (per [platform-build-and-command-line.md](references/platform-build-and-command-line.md)) as reference for `build-run-engineer` to execute, rather than running it from this role.

## 8. Edge cases & guardrails

- **Never let a test call into anything other than the Shared Core abstraction production code itself uses for time/randomness.** A `Game.Core.*` test that reads real `Time.time` or unseeded `Random` isn't testing determinism — it's hiding a violation of `coding-principles.md`'s Shared Core integrity rule behind a passing (or worse, intermittently failing) test.
- **`[UnityTest]` only supports `[ValueSource]` for parameterization — never `[TestCase]`/`[TestCaseSource]`** (per [async-coroutine-and-parameterized-tests.md](references/async-coroutine-and-parameterized-tests.md)); reaching for the wrong attribute on a coroutine test is a documented framework limitation, not a bug to work around cleverly.
- **`[UnityTest]` is incompatible with NUnit's `[Repeat]`, unsupported on WSA, and Play Mode `[Retry]` throws `InvalidCastException`** — don't combine these regardless of how reasonable they'd look in isolation.
- **Runtime-generated parameterized-test arguments don't work reliably in this package** — build parameter sources from static, compile-time-known data, not something computed at test-discovery time.
- **`ConditionalIgnoreAttribute` is real but missing from the manual's own attribute table** — don't conclude it doesn't exist, and don't skip auditing the `UnityEngine.TestTools` namespace page directly when cataloguing "every attribute available."
- **Call `LogAssert.Expect` before running the code under test, not after** — the check happens at frame end, and multiple `Expect` calls must match in the order logged.
- **`GameObject.Find`/`Object.FindObjectOfType` inside test code is an accepted UTF idiom, not a `performance-and-algorithms.md` violation** — that rule targets shipped production hot-path code; never let this precedent justify `Find` calls in `Game.Client.*`/`Game.Core.*` production code itself.
- **`UnitySetUp`/`UnityTearDown` do not re-run after a domain reload the way plain NUnit `SetUp`/`OneTimeSetUp` do** — a test that assumes otherwise after entering/exiting Play Mode mid-test will silently skip re-initialization it expected to happen.
- **`TestPlayerBuildModifierAttribute`/`ITestPlayerBuildModifier` live in namespace `UnityEditor.TestTools`, not `UnityEditor.TestTools.TestRunner.Api`** — a plausible lookup mistake when reaching for this type alongside `TestRunnerApi`/`Filter`/`ExecutionSettings`.
- **Two distinct callback interfaces exist for test-run progress** — `UnityEditor.TestTools.TestRunner.Api.ICallbacks`/`IErrorCallbacks` (Editor-only, `ITestAdaptor`/`ITestResultAdaptor`) vs. `UnityEngine.TestRunner.ITestRunCallback` (Editor **and** Player, raw NUnit `ITest`/`ITestResult`, registered via `[TestRunCallback]`) — pick based on whether the listener must run inside a built Player.
- **`TestRunnerApi`'s non-static instance methods are flagged for future obsolescence** — write new tooling against the static equivalents (`ExecuteTestRun`, `RegisterTestCallback`) per `coding-principles.md`'s Obsolete APIs rule, and don't introduce fresh call sites against the instance methods.
- **Never trigger a real platform build or spin up multiple Editor instances from this skill's own initiative** — that's `build-run-engineer`'s explicit-request-only territory; a test needing on-device verification gets flagged/handed off, not executed directly.
- **Never treat a flaky test as "probably fine" and widen the assertion tolerance to make it pass** — for `Game.Core.*` code this is almost always a sign of a Shared Core determinism violation (real time/randomness leaking in), and for `Game.Client.*` Play Mode tests it's a sign of an unaccounted-for frame-timing dependency; root-cause it rather than loosening the check.
- **This package's manual for the 2.0 experimental release is missing a few pages present in older versions** (`reference-custom-assertion.html`, `reference-attribute-conditionalignore.html`, `reference-custom-yield-instructions.html` all 404 here) — their content lives on the corresponding API pages instead (`LogAssert`, `ConditionalIgnoreAttribute`, `IEditModeTestYieldInstruction`); don't conclude a feature is undocumented just because its dedicated manual page is missing at this URL.
