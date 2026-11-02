---
name: unity-test-framework
description: "Unity Test Framework 2.0: UnityTest, UnitySetUp, LogAssert, -runTests, TestRunnerApi. Use to write or run tests."
user-invocable: false
---

# Unity Test Framework

- **Not for:** which cases to write (`risk-based-test-planning`).
- **Not for:** the CI job (`jenkins-pipeline-authoring`).
- **Not for:** the batchmode command line itself (`unity-batchmode-cli`).
- **Not for:** UI Toolkit element driving (`ui-toolkit`).
- **Not for:** Profiler measurement (`unity-profiler-diagnostics`).
- **Not for:** plain NUnit (NUnit docs).
- **Not for:** a `dotnet test` mirror of Core outside the Editor (`core-tests-without-unity`).
- **Docs:** `https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/` (API under `.../api/`) — keep `@2.0`; read the installed version from `Packages/manifest.json`.
  - **Version caveat:** the 2.0 manual lacks pages that exist in 1.x; check the API page before concluding a feature is missing.

## References
- **[authoring.md](references/authoring.md):** Creating an assembly, choosing a mode or attribute, a test spans frames or is parameterized.
- **[execution-order.md](references/execution-order.md):** A setup/teardown runs at a surprising time, state vanishes after a domain reload, or assets/files must be staged for a Player run (`PrebuildSetup`/`PostBuildCleanup`).
- **[assertions.md](references/assertions.md):** Asserting logs, floats/vectors/quaternions, allocations, or a MonoBehaviour's completion.
- **[running.md](references/running.md):** Scoping a headless run, running in a Player, or driving runs from Editor tooling.

## Steps
1. **Record the review status of the code under test:** unreviewed → still test it and say no correctness gate stands behind the results.
   - **Regression test before the fix (`/fix` step 4):** runs against unreviewed code by design.
2. **Test Core in Edit Mode:** Play Mode only for physics, timing, prefabs, scene state — Core has no `UnityEngine` dependency.
   - **`dotnet test` mirror:** an adopted mirror runs the same tests too (`core-tests-without-unity`); a pass in one runner only is not a pass.
3. **Set up the assembly and mode marker first:** per [authoring.md](references/authoring.md).
   - **Test missing from the Test Runner:** an assembly problem (missing reference, script outside a test assembly).
4. **Check the attribute against Unity's catalog:** several NUnit ones are unsupported or throw ([authoring.md](references/authoring.md)).
5. **Inject the seed and clock production code already takes:** a Core test reading real time or unseeded randomness flickers and hides a determinism violation.
6. **Use `[UnityTest]` only when the assertion needs frames to pass:**
   - **Completion is a condition:** use `MonoBehaviourTest<T>`.
7. **Parameterize with a source the attribute supports:** per [authoring.md](references/authoring.md).
   - **Unsupported sources:** silently ignored.
8. **Expect a log before the code logs it:** and compare Unity value types with the framework comparers ([assertions.md](references/assertions.md)).
9. **Gate a no-allocation claim with the allocation constraint:** not a comment.
10. **Debug setup interactions from the fixed order:** in [execution-order.md](references/execution-order.md).
11. **Scope CI runs with filters and pair `-runTests` with `-batchmode`:** per [running.md](references/running.md).
    - **Check:** the run executed more than zero tests.
12. **Fix a flaky test at its cause:** real time/randomness in Core, unaccounted frame timing in Play Mode.
    - **Tolerance:** never widen it.
13. **A repeatedly failing submission goes back through code review:** not another test pass.

## Never
- **Unsupported combinations:** combine `[UnityTest]` with `Repeat`, or use `Retry` in Play Mode — unsupported / throws.
- **Discovery-time data:** build parameter data at discovery time — use static data.
- **`TestRunnerApi` instance members:** write new tooling on them — flagged for obsolescence.
- **Scene-search calls in test code:** treat `Find*` as test-only; do not copy them into production code (banned by `csharp-standards`).
- **Players and Editors:** build a platform Player or open extra Editor instances — hand to `build-release-engineer` on the GD's explicit request.

## Output
```
## Test Work — <module>
- Test kind / assembly: <Edit Mode | Play Mode coroutine | async | MonoBehaviourTest> · <asmdef, mode marker>
- Determinism: <seed and clock injected — or "not Core code">
- Parameterization / setup hooks / log expectations: <...>
- Assertions: <comparers, allocation constraint>
- CI: <flags, filter, results path — or "local only">
```

## Example
- **"Add `TestCase` attributes to this `[UnityTest]`":** declined.
  - **Why:** only `Values`-style sources work on `[UnityTest]`; the other cases would never run while the suite stays green.
  - **Did instead:** rewrote with the supported source.
