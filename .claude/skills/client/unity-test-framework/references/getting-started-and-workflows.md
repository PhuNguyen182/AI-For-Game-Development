# Getting Started and Workflows — modes, assemblies, running tests

Sources: [Test Framework overview](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/index.html), [Edit Mode vs Play Mode tests](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/edit-mode-vs-play-mode-tests.html), [Creating tests](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/workflow-create-test.html), [Creating test assemblies](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/workflow-create-test-assembly.html), [Running tests](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/workflow-run-test.html), [What's new in 2.0](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/whats-new.html).
Covers: SKILL.md §4 — **"Test `Game.Core.*` in Edit Mode and reserve Play Mode for what needs a running frame loop"**, **"Set up the test assembly and its mode markers before writing the first test"**.

Which mode a test belongs in, and what the assembly has to reference before
the attributes compile. The game rules the tests verify live in
`Game.Core.*` and belong to `csharp-engineer`; this file is only about where
the test itself runs.

## Edit Mode against Play Mode

| Axis | Edit Mode | Play Mode | Source |
|---|---|---|---|
| What runs | The Editor, without entering play; no frame loop, no physics step | A running player loop, with frames, physics and scene lifecycle | [Edit Mode vs Play Mode tests](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/edit-mode-vs-play-mode-tests.html) |
| Right for | Pure logic with no `UnityEngine` dependency — which is exactly what Shared Core is required to be | MonoBehaviour behaviour, prefab instantiation, timing, physics, scene state | [Edit Mode vs Play Mode tests](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/edit-mode-vs-play-mode-tests.html) |
| Cost | Fast enough to run on every change | Enters play mode per run, so a suite of them is a pipeline decision rather than an inner-loop one | [Running tests](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/workflow-run-test.html) |
| Editor API access | Available — Editor-only assemblies can reference the Editor test runner | Not available in a Player run, which is what makes an Editor-only assembly a real constraint | [Creating test assemblies](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/workflow-create-test-assembly.html) |

## Assembly setup

| Subject | What it decides | Source |
|---|---|---|
| Assembly definition references | The NUnit assembly and the runtime test runner are what make the attributes compile; the Editor test runner reference is additionally required for Edit-Mode-only constructs and forces the assembly Editor-only | [Creating test assemblies](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/workflow-create-test-assembly.html) |
| Platform targeting | An assembly limited to the Editor cannot ship in a Player run, so a Play Mode suite intended to run on device must not be Editor-only | [Creating test assemblies](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/workflow-create-test-assembly.html) |
| Mode marker | Version 2.0 lets an assembly, fixture or test declare whether it needs Play Mode, so the two modes can share one assembly instead of forcing a split | [What's new in 2.0](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/whats-new.html) |
| Test folder placement | The Test Runner window creates the assembly and folder for you; a test script placed outside an assembly that references the framework simply will not be discovered | [Creating tests](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/workflow-create-test.html) |

**Critical caveat**: a test that does not appear in the Test Runner window is
almost always an assembly problem — a missing reference, or a script outside
any test assembly — not a broken attribute.

## Running

| Route | What it decides | Source |
|---|---|---|
| Test Runner window | The interactive route, with per-test and per-assembly selection; the default for local work | [Running tests](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/workflow-run-test.html) |
| Run location on a Player | Executes Play Mode tests in a built standalone player rather than the Editor, which is the only way platform-specific behaviour is exercised — see [platform-build-and-command-line.md](platform-build-and-command-line.md) | [Running Play Mode tests in a player](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/workflow-run-playmode-test-standalone.html) |
| Command line | The unattended route for CI, covered in [platform-build-and-command-line.md](platform-build-and-command-line.md) | [Running tests](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/workflow-run-test.html) |

## What version 2.0 changed

| Change | Consequence | Source |
|---|---|---|
| Play Mode requirement as a marker | Removes the need for physically separate assemblies per mode, so a new project should not split them by reflex | [What's new in 2.0](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/whats-new.html) |
| Async task tests | Async production code can be tested without wrapping it in a coroutine — see [async-coroutine-and-parameterized-tests.md](async-coroutine-and-parameterized-tests.md) | [What's new in 2.0](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/whats-new.html) |
| Experimental status | The manual page set differs from 1.x, so a missing page is a documentation move rather than a removed feature — see [root-links.md](root-links.md) | [Test Framework overview](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/index.html) |
