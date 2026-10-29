---
name: unity-test-framework
description: "Unity Test Framework 2.0: Edit/Play Mode test assemblies, UnityTest, UnitySetUp, LogAssert, Is.Not.AllocatingGCMemory, comparers, PrebuildSetup, -runTests/-testFilter, TestRunnerApi. Use when tests must be written or run."
user-invocable: false
---

# Unity Test Framework

Not for: which cases to write (`risk-based-test-planning`), the CI job (`jenkins-pipeline-authoring`), the batchmode command line itself (`unity-batchmode-cli`), UI Toolkit element driving (`ui-toolkit`), Profiler measurement (`unity-profiler-diagnostics`), plain NUnit (NUnit docs).
Docs: `https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/` (API under `.../api/`) — keep `@2.0`; read the installed version from `Packages/manifest.json`. The 2.0 manual lacks pages that exist in 1.x: check the API page before concluding a feature is missing.

| Reference | Read when |
|---|---|
| [authoring.md](references/authoring.md) | Creating an assembly, choosing a mode or attribute, a test spans frames or is parameterized |
| [execution-order.md](references/execution-order.md) | A setup/teardown runs at a surprising time, state vanishes after a domain reload, or assets/files must be staged for a Player run (`PrebuildSetup`/`PostBuildCleanup`) |
| [assertions.md](references/assertions.md) | Asserting logs, floats/vectors/quaternions, allocations, or a MonoBehaviour's completion |
| [running.md](references/running.md) | Scoping a headless run, running in a Player, or driving runs from Editor tooling |

## Steps
1. **Record the review status of the code under test** — unreviewed: still test it and say no correctness gate stands behind the results. A regression test written before the fix (`/fix` step 4) runs against unreviewed code by design.
2. **Test `Game.Core.*` in Edit Mode**; Play Mode only for physics, timing, prefabs, scene state — Core has no `UnityEngine` dependency.
3. **Set up the assembly and mode marker first**, per [authoring.md](references/authoring.md). A test missing from the Test Runner is an assembly problem (missing reference, script outside a test assembly).
4. **Check the attribute against Unity's catalog** — several NUnit ones are unsupported or throw ([authoring.md](references/authoring.md)).
5. **Inject the seed and clock production code already takes** — a Core test reading real time or unseeded randomness flickers and hides a determinism violation.
6. **Use `[UnityTest]` only when the assertion needs frames to pass**; use `MonoBehaviourTest<T>` when completion is a condition.
7. **Parameterize with a source the attribute supports** ([authoring.md](references/authoring.md)); unsupported sources are silently ignored.
8. **Expect a log before the code logs it**, and compare Unity value types with the framework comparers ([assertions.md](references/assertions.md)).
9. **Gate a no-allocation claim with the allocation constraint**, not a comment.
10. **Debug setup interactions from the fixed order** in [execution-order.md](references/execution-order.md).
11. **Scope CI runs with filters and pair `-runTests` with `-batchmode`**, per [running.md](references/running.md). Check the run executed more than zero tests.
12. **Fix a flaky test at its cause** — real time/randomness in Core, unaccounted frame timing in Play Mode. Never widen the tolerance.
13. **A repeatedly failing submission goes back through code review**, not another test pass.

## Never
- Combine `[UnityTest]` with `Repeat`, or use `Retry` in Play Mode — unsupported / throws.
- Build parameter data at discovery time — use static data.
- Write new tooling on `TestRunnerApi` instance members — flagged for obsolescence.
- Treat scene-search calls (`Find*`) in test code as test-only; do not copy them into production code (banned by csharp-standards).
- Build a platform Player or open extra Editor instances — hand to `build-release-engineer` on the GD's explicit request.

## Output
```
## Test Work — <module>
- Test kind / assembly: <Edit Mode | Play Mode coroutine | async | MonoBehaviourTest> · <asmdef, mode marker>
- Determinism: <seed and clock injected — or "not Core code">
- Parameterization / setup hooks / log expectations: <...>
- Assertions: <comparers, allocation constraint>
- CI: <flags, filter, results path — or "local only">
- Verified: <runs and result — or "not run">
- Known limitations: <...>
```
On request only, add `Latent concerns` and `Future remediation`, each with its trigger.

## Example
- "Add `TestCase` attributes to this `[UnityTest]`" → declined: only `Values`-style sources work on `[UnityTest]`; the other cases would never run while the suite stays green. Rewrote with the supported source.
