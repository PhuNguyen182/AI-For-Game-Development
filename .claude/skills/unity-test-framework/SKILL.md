---
name: unity-test-framework
description: >
  Technique for Unity's Test Framework package (`UnityEngine.TestTools`,
  `UnityEditor.TestTools.TestRunner.Api`) — a customised NUnit integration for
  Edit Mode and Play Mode tests: test assemblies, `UnityTest` coroutine tests,
  async task tests, `UnitySetUp` and `UnityTearDown`, `RequiresPlayMode`,
  `ConditionalIgnore`, `PrebuildSetup`, `LogAssert`, the `Utils` equality
  comparers, allocation `Constraints`, `MonoBehaviourTest<T>`, the Test Runner
  window, the `-runTests` command line, and `TestRunnerApi`. Use when tests
  must be written, scoped, or run. Not for: the game rules under test
  (`csharp-engineer`); manual walkthroughs against the GDD
  (`playtest-tester`); real platform builds (`build-run-engineer`); Profiler
  measurement (`unity-profiler-diagnostics`); plain NUnit fundamentals
  (NUnit's own documentation).
---

# Unity Test Framework — Edit Mode, Play Mode, Assertions, CI

## Bundled resources

### References
Read-only context, loaded on demand so SKILL.md itself stays short.

| File | Contents | Read when |
|---|---|---|
| [root-links.md](references/root-links.md) | Package and NUnit roots, the version pin, and the pages that do not exist at this version | Starting any task here, or a documentation page fails to resolve |
| [getting-started-and-workflows.md](references/getting-started-and-workflows.md) | Edit Mode against Play Mode, assembly setup, running tests, version 2.0 changes | Creating a test assembly or deciding which mode a test belongs in |
| [attributes-reference.md](references/attributes-reference.md) | The Unity-authored attribute catalog and what each one changes about execution | Choosing an attribute, or checking whether an NUnit one applies here |
| [execution-order-and-setup-cleanup.md](references/execution-order-and-setup-cleanup.md) | Build-time setup and cleanup, outer actions, the full order, domain-reload rules | A setup or teardown runs at a surprising time |
| [async-coroutine-and-parameterized-tests.md](references/async-coroutine-and-parameterized-tests.md) | Coroutine tests, async task tests, parameterization sources, Edit Mode yield instructions | A test spans frames, awaits, or needs several cases |
| [assertions-logging-and-monobehaviour-testing.md](references/assertions-logging-and-monobehaviour-testing.md) | `LogAssert`, equality comparers, allocation constraints, `MonoBehaviourTest<T>` | Asserting on logs, floats, vectors, or allocations |
| [platform-build-and-command-line.md](references/platform-build-and-command-line.md) | Platform attributes, standalone Player runs, the full command-line surface | Wiring CI, or scoping a headless run |
| [scripting-api-test-runner-api.md](references/scripting-api-test-runner-api.md) | `TestRunnerApi`, `Filter`, `ExecutionSettings`, and the two callback interfaces | Building Editor tooling that drives test runs |

## 1. Objective
Produce tests that fail only when the code is wrong. The failures this prevents are the ones that make a suite worthless: a `Game.Core.*` test that reads real time or unseeded randomness and passes intermittently, a coroutine test parameterized with an attribute the framework silently ignores, a log expectation registered after the code already logged, a float comparison that fails on precision rather than on behaviour, and a setup method assumed to re-run after a domain reload that it does not survive.

## 2. Role
Act as the automated-testing specialist for the QA track, testing client-track code — the tool reached for once code has passed Code Review and needs a verification gate. You choose the test kind, the attributes, and the assertions; you do not author the game rules being verified, walk the game manually against the design, or build for a device. `qa-automation-engineer` uses this skill to author and run tests in the Editor; `build-verification-tester` uses only its standalone-Player and command-line surface to run the existing suite against a real build.

## 3. When to invoke this skill
- Creating a test assembly or a test script, and deciding whether it targets Edit Mode, Play Mode, or both.
- Writing Edit Mode unit tests against `Game.Core.*` logic that has already passed review.
- Writing Play Mode integration tests against MonoBehaviour, scene, physics, or multi-frame behaviour.
- A test must span frames, await an async operation, or enter and leave Play Mode partway through.
- Parameterizing a test, or conditionally skipping one by runtime condition, platform, or argument.
- Asserting that the code under test logs something specific, or logs nothing unexpected.
- Wiring headless CI runs and consuming the resulting NUnit XML report.
- Building Editor tooling that drives test runs programmatically.
- A test is flaky, or passes for a reason nobody can name.
- Negative trigger: authoring the game rule the test verifies — damage formulas, state machines, economy maths — that is `csharp-engineer`'s Shared Core, per `coding-principles.md`'s Shared Core integrity rule.
- Negative trigger: walking Play Mode by hand and comparing feel against the GDD — that is `playtest-tester`, a different activity that happens to share Play Mode with this one.
- Negative trigger: producing a real platform build or running several Editor instances — that is `build-run-engineer`, and only on the GD's explicit request. Running the existing suite against an artifact that already exists is `build-verification-tester`, which uses this skill's standalone-Player and command-line coverage.
- Negative trigger: measuring frame time, GC pressure, or memory — that is `unity-profiler-diagnostics`; the allocation constraint here is a pass-or-fail gate, not a measurement.
- Negative trigger: plain NUnit attributes and assertion style that are not Unity additions — defer to NUnit's own documentation rather than restating it.

## 4. How to use this skill
1. **Confirm the code under test has already passed Code Review** — these tests are a gate on reviewed code, not a substitute for review, and a suite written against code that is about to change is work done twice.
2. **Test `Game.Core.*` in Edit Mode and reserve Play Mode for what needs a running frame loop** — Shared Core has no `UnityEngine` dependency, so it needs no scene, no MonoBehaviour host, and no Play Mode at all, per [getting-started-and-workflows.md](references/getting-started-and-workflows.md) and the version pin in [root-links.md](references/root-links.md). Play Mode is for physics, timing, prefab instantiation and scene state.
3. **Set up the test assembly and its mode markers before writing the first test** — the assembly's references decide which attributes even compile, and the mode marker decides where each test runs, per [getting-started-and-workflows.md](references/getting-started-and-workflows.md). Splitting assemblies purely to separate the two modes is no longer necessary, so do it only where the project already works that way.
4. **Pick the attribute from Unity's own catalog rather than assuming an NUnit equivalent applies** — several NUnit attributes are unsupported or throw here, and at least one Unity attribute is absent from the manual's own table while existing in the API, per [attributes-reference.md](references/attributes-reference.md). Check before writing, not after a confusing failure.
5. **Inject the seed and the clock production code already takes** — a Core test that reads real time or unseeded randomness is not testing determinism, it is concealing a violation of `coding-principles.md`'s Shared Core integrity rule behind a result that will eventually flicker.
6. **Reach for a coroutine test only when the assertion genuinely spans frames** — a same-frame check wrapped in a frame yield is slower and no more correct, per KISS in `coding-principles.md`. Use the MonoBehaviour test wrapper when completion is naturally a condition rather than a fixed number of frames, per [async-coroutine-and-parameterized-tests.md](references/async-coroutine-and-parameterized-tests.md).
7. **Parameterize with the source the chosen test attribute actually supports** — the coroutine attribute accepts only one of the parameterization sources, and the others are ignored rather than rejected, per [async-coroutine-and-parameterized-tests.md](references/async-coroutine-and-parameterized-tests.md). Build cases from static data, since arguments computed at discovery time are unreliable here.
8. **Settle the execution order before debugging a setup interaction** — the Unity setup and teardown hooks interleave with NUnit's own in a fixed order, and they do not resume the way plain NUnit hooks do after a domain reload, per [execution-order-and-setup-cleanup.md](references/execution-order-and-setup-cleanup.md). Most "the fixture is wrong" reports are this.
9. **Expect a log before the code under test emits it** — the expectation is checked at frame end and matched in the order logged, so registering it afterwards fails, per [assertions-logging-and-monobehaviour-testing.md](references/assertions-logging-and-monobehaviour-testing.md). An unexpected error log fails the test on its own, which is a feature rather than noise.
10. **Compare Unity value types through the framework's own comparers** — floats, vectors, quaternions and colours need a tolerance the default equality does not apply, and hand-rolled epsilon checks in every assertion are what the comparers exist to replace.
11. **Gate a no-allocation claim with an allocation constraint rather than a review note** — it turns `performance-and-algorithms.md`'s hot-path rule into a regression gate that survives the next refactor, which a comment does not.
12. **Scope a CI run with filters, and pair the run flag with batch mode** — running the whole suite for every change wastes the pipeline's time, and the results file is standard NUnit XML that CI can parse directly, per [platform-build-and-command-line.md](references/platform-build-and-command-line.md).
13. **Reach for `TestRunnerApi` only for genuine Editor tooling, and only through its static members** — the Test Runner window and the command line cover routine runs, and the instance members are flagged for future obsolescence, per `coding-principles.md`'s Obsolete APIs section and [scripting-api-test-runner-api.md](references/scripting-api-test-runner-api.md).
14. **Root-cause a flaky test rather than widening its tolerance** — in Core code it almost always means real time or randomness leaked in, and in Play Mode it means an unaccounted frame-timing dependency. A loosened assertion converts a real defect into a test that can no longer find it.

## 5. Specific goals / tasks this skill performs
- Creating and configuring test assemblies and test scripts for Edit Mode, Play Mode, or both.
- Writing Edit Mode unit tests against Shared Core logic with injected seeds and clocks.
- Writing Play Mode integration tests, coroutine tests, async task tests, and MonoBehaviour condition tests.
- Parameterizing tests correctly for the attribute in use, and conditionally ignoring cases.
- Asserting on expected and unexpected log output, on Unity value types, and on allocation behaviour.
- Building pre-build setup and post-build cleanup steps with the correct execution order.
- Wiring headless CI runs and consuming the NUnit XML report.
- Building Editor tooling on `TestRunnerApi`.
- Writing network-condition cases once the backend track is active, with the same mechanics.
- Out of scope: the game rules under test (`csharp-engineer`); manual GDD walkthroughs (`playtest-tester`); platform builds and multi-instance runs (`build-run-engineer`, on explicit request only); Profiler measurement (`unity-profiler-diagnostics`); plain NUnit fundamentals (NUnit's own documentation).

## 6. Output format
```
## Test Work — <module or feature under test>
- Code Review status of the code under test: <confirmed passed>
- Test kind: <Edit Mode / Play Mode coroutine / async task / MonoBehaviour condition>
- Assembly: <name, references, mode marker usage>
- Determinism: <seed and clock injected through the production abstraction — or "not Core code">
- Parameterization: <source used, and why it suits the attribute — or "single case">
- Setup and cleanup: <hooks used, and any domain-reload consequence>
- Log expectations: <registered before the code runs — or "none">
- Assertions: <comparers used for value types, allocation constraint if any>
- CI: <flags, filter scope, results path — or "local runs only">
- Flakiness: <confirmed deterministic across repeated runs, or the root cause found>
- Layer: <Editor-only test assembly / Play Mode assembly / both>
- Known limitations: <...>
```

**Extended report — emit ONLY when the requester asks for it.** It replaces the one-line `Known limitations` above with all three fields:
```
- Known limitations: <what the suite does not cover>
- Latent concerns: <failure modes not yet triggered: paths untested, platform-conditional cases skipped, trade-offs knowingly deferred>
- Future remediation: <the concrete fix for each concern above, each with the condition that should trigger it>
```

## 7. Examples
**Example 1**
- Input: "Write Edit Mode tests for the ability-cooldown logic in Shared Core that just passed review."
- Output: an Editor-only test assembly with plain tests — no Play Mode needed, since the type has no `UnityEngine` dependency. Time comes from the same clock abstraction production code takes, with a fixed value per case, so expiry, refresh and the exact edge of the window are all assertable without waiting on anything real. No log expectations or setup hooks, because nothing in this path logs or touches the scene.

**Example 2**
- Input: "Add cases to this coroutine test with `TestCase` attributes."
- Output: declined — the coroutine test attribute supports only one parameterization source, and the others are ignored rather than reported, so the extra cases would never have run while the suite still showed green. Rewrote the cases against the supported source, and left a note that a non-coroutine test would accept the original form if the assertion turns out not to need frames after all.

**Example 3**
- Input: "The fixture works in Edit Mode but the state is gone once the test enters Play Mode."
- Output: the Unity setup hook does not resume after the domain reload that entering Play Mode triggers, unlike a plain NUnit setup, so everything established before the yield was lost while everything after it appeared to run normally. Moved the state the test depends on to after the transition, and confirmed the order against [execution-order-and-setup-cleanup.md](references/execution-order-and-setup-cleanup.md) rather than inferring it from the symptom.

**Example 4**
- Input: "Can we run this feature's tests on the actual Android build as part of QA?"
- Output: documented the standalone-Player run and the platform and build-path flags, and split the work — producing the APK is `build-run-engineer`'s territory and needs the GD's explicit request, while running the suite against that artifact once it exists is `build-verification-tester`'s. This skill supplied the configuration for both rather than triggering the build itself.

## 8. Edge cases & guardrails
- Never let a Core test read real time or unseeded randomness — it hides a determinism violation behind a result that eventually flickers.
- Never widen an assertion tolerance to quiet a flaky test — find what is non-deterministic instead.
- Never parameterize a coroutine test with an unsupported source — the cases silently do not run and the suite still reports success.
- Never combine the coroutine attribute with NUnit's repeat attribute, and never use the retry attribute in Play Mode — one is unsupported and the other throws.
- Never build parameterized arguments from data computed at discovery time — use static, compile-time-known sources.
- Never register a log expectation after the code under test has run — the check happens at frame end and matches in order.
- Never compare floats or Unity value types with default equality — use the framework's comparers, or the test fails on precision instead of behaviour.
- Never assume the Unity setup hook resumes after a domain reload the way NUnit's does — it does not, and the omission is silent.
- Never conclude a feature is undocumented because its manual page is missing at this package version — several pages moved onto their API pages, per [root-links.md](references/root-links.md).
- Never write new tooling against `TestRunnerApi`'s instance members — they are flagged for obsolescence, per `coding-principles.md`'s Obsolete APIs section.
- Never let scene-search calls used inside test code become a precedent for production code — that idiom is accepted here and banned there by `performance-and-algorithms.md`.
- Never trigger a platform build or spin up extra Editor instances from this skill — flag the need and hand it to `build-run-engineer`, who acts only on the GD's explicit request.
- Never re-test a repeatedly failing submission without routing it back through Code Review first — a fix that looks small is exactly the one that skips the gate.
