# Getting Started & Workflows

Source pages: [Overview](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/index.html), [Features](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/utf-features.html), [Edit Mode vs. Play Mode tests](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/edit-mode-vs-play-mode-tests.html), [Workflow: Creating tests](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/workflow-create-test.html), [Workflow: Creating test assemblies](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/workflow-create-test-assembly.html), [Workflow: Running tests](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/workflow-run-test.html), [Workflow: Running Play Mode tests in a player](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/workflow-run-playmode-test-standalone.html), [What's new in 2.0](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/whats-new.html), [Upgrade Guide](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/upgrade-guide.html).

## Overview

Unity Test Framework (UTF) is a package (`com.unity.test-framework`) built on a **customized NUnit 3.5 integration**, for testing code in both **Edit Mode** and **Play Mode**, on target platforms including Standalone, Android, and iOS. The docs explicitly say to read the NUnit documentation alongside UTF's own, since many attributes/behaviors UTF exposes (`Test`, `TestCase`, `TestCaseSource`, `ValueSource`, `SetUp`, `TearDown`, `Ignore`, `Assert.*`) are plain NUnit, only partially re-documented on Unity's own pages.

**Prerequisite knowledge assumed by the docs:**
1. **Assemblies** — tests live in Test Assemblies configured via `.asmdef` files that set platform targets and assembly references.
2. **NUnit** — general NUnit API knowledge, on top of UTF's own extensions.
3. **TDD / unit testing basics** — Arrange-Act-Assert, attribute-driven test phases.

**Requirements:** Unity Editor 2019.2 or later.

**Installation:** via Package Manager, search "Test Framework"; in 2019.2+ you may need to explicitly enable the package.

## Known limitations (as documented for this version)

- `[UnityTest]` is **not supported on the WSA platform**.
- `[UnityTest]` does **not** fully support parameterized tests — only `[ValueSource]` works with it (see [async-coroutine-and-parameterized-tests.md](async-coroutine-and-parameterized-tests.md)); `[TestCase]`/`[TestCaseSource]` do not.
- `[UnityTest]` is **not compatible with NUnit's `[Repeat]`** attribute.
- **Nested test fixtures cannot run from the Editor UI.**
- Play Mode tests using NUnit's **`[Retry]`** attribute throw an `InvalidCastException`.
- Tests with **runtime-generated parameters fail**.
- The Test Runner's tree shows pre-run state; a test gated behind a preprocessor directive (`#if UNITY_ANDROID`) still executes but its result may not display in the tree — put only the method **body** behind the `#if`, not the whole method/attribute, to work around this.

## Edit Mode vs. Play Mode tests

- **Edit Mode tests** run only in the Editor. They can access both Editor and game code, and execute inside the `EditorApplication.update` callback loop. They can use `[UnityTest]` for multi-frame/yield-based tests, and can programmatically enter/exit Play Mode from within a test (see [async-coroutine-and-parameterized-tests.md](async-coroutine-and-parameterized-tests.md) for `EnterPlayMode`/`ExitPlayMode`).
- **Play Mode tests**, when written with `[UnityTest]`, run as a coroutine at runtime. They run in the Editor's built-in Play Mode by default, or in a standalone Player, and exercise actual game code.

**Assembly (`.asmdef`) requirements:**
- Both kinds of test assemblies must reference `nunit.framework.dll`.
- An **Edit Mode** assembly either restricts `includePlatforms` to `Editor`, or (if it also targets other platforms) tags individual tests `[RequiresPlayMode(false)]` so they stay in Edit Mode rather than running in Play Mode.
- A **Play Mode** assembly must reference the assemblies containing the code under test. Example asmdef fragment: `"references": ["NewAssembly"], "optionalUnityReferences": ["TestAssemblies"], "includePlatforms": []`.

**`[RequiresPlayMode]` — the 2.0 mechanism that removes the old separate-assembly requirement:**
- Apply `[RequiresPlayMode]` to a test in an **Editor-only** assembly so it runs in the Editor's Play Mode instead of Edit Mode.
- Apply `[RequiresPlayMode(false)]` to a test in a **platform-targeted** assembly so it's excluded from Play Mode and runs in Edit Mode instead.
- **A test run "On Player" always runs in the Player regardless of `[RequiresPlayMode]`/assembly platform settings** — that combination can't override an explicit Player run.

## Workflow: Creating a test assembly

Two equivalent ways to create a Test Assembly folder:
- **Test Runner window** (`Window > General > Test Runner`) → with an Assets folder selected → "Create a new Test Assembly Folder in the active path".
- **Assets menu** → with an Assets folder selected → `Assets > Create > Testing > Test Assembly Folder`.

Both generate a folder named `Tests` (or `Tests 1`, `Tests 2`, … for subsequent ones) containing an auto-generated `.asmdef` that references `nunit.framework.dll`, `UnityEngine.TestRunner`, and (Edit Mode only) `UnityEditor.TestRunner`.

**Platform checkbox default behavior:**
- **Editor only** (the default when created from the Test Runner) → Edit Mode tests.
- **Any Platform**, or a specific non-Editor platform → Play Mode tests by default.

**Gotchas:**
- The **`UnityEditor.TestRunner`** reference is only available/valid for Edit Mode tests.
- Renaming the `.asmdef` **file** does not change its internal `Name` property — edit the Inspector or the file's `name` field directly.
- Each assembly's `Name` must be unique project-wide.

## Workflow: Creating a test script

- **Test Runner window** → "Create a new Test Script in the active path" (with a Test Assembly folder selected), or
- **Assets menu** → `Assets > Create > Testing > C# Test Script`.

Both generate `NewTestScript.cs` pre-populated with a sample test; rename it in-place.

The process is identical for Edit Mode and Play Mode tests. For Play Mode specifically:
- A test targeting Standalone/another platform belongs in an assembly that references that platform.
- A Play Mode test that lives in an **Editor-only** assembly needs `[RequiresPlayMode]` to actually run in Play Mode there.

**Important build-pipeline note:** Unity does **not** include test assemblies (NUnit, UTF, and user test scripts) in a normal player build — they're only included when the Test Runner's **Run Location** is set to **On Player**. Test code never ships in a normal production build by default.

## Workflow: Running tests in the Test Runner window

Ways to run tests:
1. Double-click a test or fixture name.
2. **Run All** / **Run Selected** buttons at the bottom of the window.
3. Right-click any tree item → **Run** (runs it and its children).

Filtering what's shown/run:
- Text search box.
- Click a specific class/fixture in the tree.
- Result-status icon toggle buttons (top-right) to filter pass/fail/etc.
- **EditMode**/**PlayMode** checkboxes to include or exclude by mode.

Command-line and CI usage is covered in full in [platform-build-and-command-line.md](platform-build-and-command-line.md); the JetBrains Rider integration is documented separately by JetBrains, not by this skill.

## Workflow: Running Play Mode tests in a standalone Player

- In the Test Runner window, set **Run Location** to **On Player**. Unity builds and runs a Player for whatever platform is currently active in **File > Build Settings** (shown in brackets on the button, e.g. "On Player (StandaloneWindows64)").
- The Editor and the running Player **must be on the same network** — results are reported back over the network, and if the connection can't be established you may see the tests pass inside the running application with no XML results produced in the Editor.
- Some platforms don't support `Application.Quit` shutting the app down — the Player keeps running after reporting results on those platforms.
- Project-role note: per this project's team structure, only `build-run-engineer` produces real platform builds when explicitly requested by the GD. `qa-automation-engineer` runs tests inside a single Editor instance and never triggers a build itself — treat this "On Player"/standalone workflow as reference material for when a Complex-tier feature's Tech Spec explicitly calls for device-level test verification, not as this skill's default recommended path.

## What's new in 2.0

- **`[RequiresPlayMode]`** — see above; removes the old hard requirement to keep Edit Mode and Play Mode tests in physically separate assemblies.
- **`[ParameterizedIgnore]`** — ignore a parameterized test case based on the specific arguments it was called with (see [async-coroutine-and-parameterized-tests.md](async-coroutine-and-parameterized-tests.md)).
- **Async `Task`-based test support** — writing tests as `async Task` methods (see [async-coroutine-and-parameterized-tests.md](async-coroutine-and-parameterized-tests.md)). Flagged as an experimental feature (the docs' `-exp` version tag) at the time these docs were fetched — validate current behavior against whatever UTF version the project has actually installed.
- **Redesigned Test Runner UI** — the previously separate Edit Mode/Play Mode tabs are merged into one view; **Run Selected** now also works for a Player-based run.

## Upgrade guide

Verbatim: "You do not need to take any actions to upgrade your project to this package version." Consult the [Changelog](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/changelog/CHANGELOG.html) for the itemized diff between versions rather than expecting a migration checklist on this page.
