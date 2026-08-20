# Unity Test Framework Documentation — Source Pages

This skill was built from the official Unity Test Framework (`com.unity.test-framework`) package documentation at version `2.0` (docs served as `2.0.1-exp.2`, an experimental release — confirm current behavior against a newer version's manual if the project has since upgraded past 2.0). Every link below was verified by fetching the live page, not assumed from memory. Pages are grouped by topic, matching the `references/` files in this skill.

## Manual — Getting started & workflow ([getting-started-and-workflows.md](getting-started-and-workflows.md))
- [Unity Test Framework overview](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/index.html) — prerequisites, installation, requirements, known limitations.
- [Unity Test Framework Features](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/utf-features.html) — feature hub linking to every other manual/API page.
- [Edit Mode vs. Play Mode tests](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/edit-mode-vs-play-mode-tests.html)
- [Workflow: Creating tests](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/workflow-create-test.html)
- [Workflow: Creating test assemblies](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/workflow-create-test-assembly.html)
- [Workflow: Running tests](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/workflow-run-test.html)
- [Workflow: Running Play Mode tests in a player](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/workflow-run-playmode-test-standalone.html)
- [What's new in version 2.0](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/whats-new.html)
- [Upgrade Guide](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/upgrade-guide.html)
- [Changelog](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/changelog/CHANGELOG.html)

## Manual — Attributes reference ([attributes-reference.md](attributes-reference.md))
- [Custom attributes](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/reference-custom-attributes.html) — the manual's attribute table (13 rows; note `ConditionalIgnore` is missing from this table despite existing in the API — see below).

## Manual — Execution order, setup/cleanup ([execution-order-and-setup-cleanup.md](execution-order-and-setup-cleanup.md))
- [Setup and cleanup at build time](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/reference-setup-and-cleanup.html) — `IPrebuildSetup`/`IPostBuildCleanup`.
- [Actions outside tests](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/reference-actions-outside-tests.html) — `UnitySetUp`/`UnityTearDown`, `IOuterUnityTestAction`, the 12-step action execution order, domain-reload behavior.

## Manual — Async, coroutine & parameterized tests ([async-coroutine-and-parameterized-tests.md](async-coroutine-and-parameterized-tests.md))
- [Parameterized tests](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/reference-tests-parameterized.html)
- Async tests (Task-based, added in 2.0) — `https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/reference-async-tests.html`
- [`UnityEngine.TestTools.UnityTestAttribute`](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEngine.TestTools.UnityTestAttribute.html) API page (coroutine-style tests, with code samples).
- [`UnityEngine.TestTools.IEditModeTestYieldInstruction`](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEngine.TestTools.IEditModeTestYieldInstruction.html) — custom Edit Mode yield instructions; the corresponding manual page (`reference-custom-yield-instructions.html`) 404s on this package version, so this API page is the only source.

## Manual/API — Assertions, logging & MonoBehaviour testing ([assertions-logging-and-monobehaviour-testing.md](assertions-logging-and-monobehaviour-testing.md))
- [`UnityEngine.TestTools.LogAssert`](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEngine.TestTools.LogAssert.html) — there is no separate manual "assertions" page in 2.0 (unlike 1.x's `reference-custom-assertion.html`, which 404s here); `utf-features.html` links straight to this API page.
- [`UnityEngine.TestTools.Constraints`](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEngine.TestTools.Constraints.html) — custom NUnit `Assert.That` constraints.
- [`UnityEngine.TestTools.Utils`](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEngine.TestTools.Utils.html) — equality comparers for `Color`/`Float`/`Quaternion`/`Vector2`/`Vector3`/`Vector4`.
- [`UnityEngine.TestTools.MonoBehaviourTest-1`](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEngine.TestTools.MonoBehaviourTest-1.html) (generic `MonoBehaviourTest<T>`) and [`IMonoBehaviourTest`](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEngine.TestTools.IMonoBehaviourTest.html).
- [`UnityEngine.TestTools.ConditionalIgnoreAttribute`](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEngine.TestTools.ConditionalIgnoreAttribute.html)
- [`UnityEngine.TestTools.TestMustExpectAllLogsAttribute`](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEngine.TestTools.TestMustExpectAllLogsAttribute.html)
- [`UnityEngine.TestTools.PreservedValuesAttribute`](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEngine.TestTools.PreservedValuesAttribute.html)

## Manual/API — Platform, build & command line ([platform-build-and-command-line.md](platform-build-and-command-line.md))
- [`UnityEngine.TestTools.UnityPlatformAttribute`](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEngine.TestTools.UnityPlatformAttribute.html)
- [`UnityEditor.TestTools.RequirePlatformSupportAttribute`](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEditor.TestTools.RequirePlatformSupportAttribute.html)
- [`UnityEngine.TestTools.RequiresPlayModeAttribute`](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEngine.TestTools.RequiresPlayModeAttribute.html)
- [`UnityEditor.TestTools.TestPlayerBuildModifierAttribute`](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEditor.TestTools.TestPlayerBuildModifierAttribute.html) and [`ITestPlayerBuildModifier`](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEditor.TestTools.ITestPlayerBuildModifier.html) — note: namespace `UnityEditor.TestTools`, **not** `UnityEditor.TestTools.TestRunner.Api`.
- [Workflow: Running Play Mode tests in a player](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/workflow-run-playmode-test-standalone.html) (also listed above)
- [Test Framework command line arguments](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/reference-command-line.html)

## API — `TestRunnerApi` programmatic test running ([scripting-api-test-runner-api.md](scripting-api-test-runner-api.md))
- [Namespace `UnityEditor.TestTools.TestRunner.Api`](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEditor.TestTools.TestRunner.Api.html)
- [`TestRunnerApi`](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEditor.TestTools.TestRunner.Api.TestRunnerApi.html)
- [`Filter`](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEditor.TestTools.TestRunner.Api.Filter.html)
- [`ExecutionSettings`](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEditor.TestTools.TestRunner.Api.ExecutionSettings.html)
- [`ICallbacks`](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEditor.TestTools.TestRunner.Api.ICallbacks.html) / [`IErrorCallbacks`](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEditor.TestTools.TestRunner.Api.IErrorCallbacks.html)
- [`ITestAdaptor`](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEditor.TestTools.TestRunner.Api.ITestAdaptor.html) / [`ITestResultAdaptor`](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEditor.TestTools.TestRunner.Api.ITestResultAdaptor.html)
- [`ITestRunSettings`](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEditor.TestTools.TestRunner.Api.ITestRunSettings.html)
- [`AssemblyType`](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEditor.TestTools.TestRunner.Api.AssemblyType.html) / [`RunState`](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEditor.TestTools.TestRunner.Api.RunState.html) / [`TestMode`](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEditor.TestTools.TestRunner.Api.TestMode.html) / [`TestStatus`](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEditor.TestTools.TestRunner.Api.TestStatus.html)
- [`CustomRunnerBase`](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEditor.TestTools.TestRunner.Api.CustomRunnerBase.html) / [`RunnerNotFoundException`](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEditor.TestTools.TestRunner.Api.RunnerNotFoundException.html)
- [Namespace `UnityEngine.TestRunner`](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEngine.TestRunner.html) — [`ITestRunCallback`](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEngine.TestRunner.ITestRunCallback.html) and [`TestRunCallbackAttribute`](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEngine.TestRunner.TestRunCallbackAttribute.html) — the raw NUnit-level callback pair, **distinct** from `ICallbacks` above (see that reference file's caveats section).

## API namespace index pages
- [`api/index.html`](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/index.html) — package API root.
- [`UnityEngine.TestTools`](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEngine.TestTools.html) — Unity's NUnit-extension attributes/interfaces/enums for authoring tests (Editor + Player).
- [`UnityEditor.TestTools.TestRunner.Api`](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEditor.TestTools.TestRunner.Api.html) — programmatic test running (Editor-only).
- [`UnityEditor.TestTools`](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEditor.TestTools.html) — Editor-only build-modification attributes/interfaces for the test Player.
- [`UnityEngine.TestRunner`](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEngine.TestRunner.html) — low-level NUnit test-progress callback interface, available in Editor and Player.

## Confirmed 404s / not present in this package version (2.0)
These plausible-looking pages do **not** exist for `com.unity.test-framework@2.0` (they existed in the 1.x manual, or exist in the newer Unity-Manual-merged docs for 6000.x Editor versions) — don't link to them, and don't assume their content is missing just because it isn't documented here (it's covered by the API pages instead):
- `manual/reference-custom-assertion.html` — content lives on the `LogAssert` API page instead.
- `manual/reference-attribute-conditionalignore.html` — content lives on the `ConditionalIgnoreAttribute` API page instead.
- `manual/reference-custom-yield-instructions.html` — content lives on the `IEditModeTestYieldInstruction` API page instead.
- `manual/TableOfContents.json` — no exposed sidebar JSON at that path.

## Prerequisite, non-Unity-specific references (consult, don't duplicate)
- [NUnit](https://nunit.org/) / [NUnit documentation](https://docs.nunit.org/) — UTF is a customized NUnit 3.5 integration; core NUnit attributes (`Test`, `TestCase`, `TestCaseSource`, `ValueSource`, `SetUp`, `TearDown`, `Ignore`, `Assert.*`) are NUnit's own and only partially re-documented on Unity's pages.
- [NUnit — Parameterized Tests](https://docs.nunit.org/articles/nunit/technical-notes/usage/Parameterized-Tests.html), [`TestCase`](https://docs.nunit.org/articles/nunit/writing-tests/attributes/testcase.html), [`ValueSource`](https://docs.nunit.org/articles/nunit/writing-tests/attributes/valuesource.html), [`Repeat`](https://docs.nunit.org/articles/nunit/writing-tests/attributes/repeat.html) (not supported by `UnityTest`), [`Retry`](https://docs.nunit.org/articles/nunit/writing-tests/attributes/retry.html) (throws `InvalidCastException` in Play Mode)
- [NUnit — SetUp and TearDown](https://docs.nunit.org/articles/nunit/technical-notes/usage/SetUp-and-TearDown.html), [`IApplyToContext`](https://docs.nunit.org/articles/nunit/extending-nunit/IApplyToContext-Interface.html), [`ICommandWrapper` (`IWrapSetUpTearDown`/`IWrapTestMethod`)](https://docs.nunit.org/articles/nunit/extending-nunit/ICommandWrapper-Interface.html), [NUnit Action Attributes](https://docs.nunit.org/articles/nunit/extending-nunit/Action-Attributes.html)
- [NUnit Test-Result XML Format](https://docs.nunit.org/articles/nunit/technical-notes/usage/Test-Result-XML-Format.html) — the schema written by `-testResults`.
- [Assembly Definition Files (Unity Manual)](https://docs.unity3d.com/Manual/ScriptCompilationAssemblyDefinitionFiles.html)
- [`BuildTarget` (Script Reference)](https://docs.unity3d.com/ScriptReference/BuildTarget.html) — values accepted by `-testPlatform` and `Filter.targetPlatform`/`ExecutionSettings.targetPlatform`.
- [Configurable Enter Play Mode (Unity Manual)](https://docs.unity3d.com/Manual/ConfigurableEnterPlayMode.html)
- [Build Settings (Unity Manual)](https://docs.unity3d.com/Manual/BuildSettings.html)
