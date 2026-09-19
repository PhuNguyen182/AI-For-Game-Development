# TestRunnerApi — driving test runs from Editor tooling

Sources: [TestRunner.Api namespace](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEditor.TestTools.TestRunner.Api.html), [TestRunnerApi](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEditor.TestTools.TestRunner.Api.TestRunnerApi.html), [Filter](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEditor.TestTools.TestRunner.Api.Filter.html), [ExecutionSettings](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEditor.TestTools.TestRunner.Api.ExecutionSettings.html), [ICallbacks](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEditor.TestTools.TestRunner.Api.ICallbacks.html), [ITestRunCallback](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEngine.TestRunner.ITestRunCallback.html).
Covers: SKILL.md §4 — **"Reach for `TestRunnerApi` only for genuine Editor tooling, and only through its static members"**.

The programmatic entry point, for tooling that has to start runs or react to
results. Routine runs belong in the Test Runner window or on the command line
covered in [platform-build-and-command-line.md](platform-build-and-command-line.md).

## Entry point

| Member | Effect | Source |
|---|---|---|
| Execute a test run | Starts a run from settings you supply, which is how a custom Editor window or a build step triggers tests | [TestRunnerApi](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEditor.TestTools.TestRunner.Api.TestRunnerApi.html) |
| Register a test callback | Subscribes a listener to run progress and results | [TestRunnerApi](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEditor.TestTools.TestRunner.Api.TestRunnerApi.html) |
| Retrieve the test tree | Enumerates discovered tests without running them, for tooling that presents or validates the suite | [TestRunnerApi](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEditor.TestTools.TestRunner.Api.TestRunnerApi.html) |

**Critical caveat**: the instance members are flagged for future
obsolescence. Write new tooling against the static equivalents, per
`coding-principles.md`'s Obsolete APIs section — this is the whole reason to
check before copying an older example.

## Scoping a run

| Type or member | What it decides | Source |
|---|---|---|
| Filter by test names | Exact full names, the programmatic form of the command line's name filter | [Filter](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEditor.TestTools.TestRunner.Api.Filter.html) |
| Filter by group | A regular expression over full names, for a whole namespace or fixture | [Filter](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEditor.TestTools.TestRunner.Api.Filter.html) |
| Filter by category and assembly | Narrows to categories or named assemblies; several filter fields combine restrictively, so an over-specified filter runs nothing | [Filter](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEditor.TestTools.TestRunner.Api.Filter.html) |
| Test mode on the filter | Edit Mode or Play Mode, and it must agree with the assemblies being filtered or the run is empty | [Filter](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEditor.TestTools.TestRunner.Api.Filter.html) |
| Execution settings | Carries the filters plus the target platform and Player-run options, which is what turns an Editor run into a device run | [ExecutionSettings](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEditor.TestTools.TestRunner.Api.ExecutionSettings.html) |

## The two callback interfaces

| Interface | Runs in | Receives | Source |
|---|---|---|---|
| Editor callbacks | The Editor only | Adaptor types wrapping the test and its result, which carry Unity-specific metadata | [ICallbacks](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEditor.TestTools.TestRunner.Api.ICallbacks.html) |
| Editor error callbacks | The Editor only | The same, plus a hook for run-level failures the ordinary callbacks never see | [ICallbacks](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEditor.TestTools.TestRunner.Api.ICallbacks.html) |
| Run callback registered by attribute | Editor and a built Player | Raw NUnit test and result objects, with no adaptor layer | [ITestRunCallback](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEngine.TestRunner.ITestRunCallback.html) |

The choice between them is whether the listener has to run inside a built
Player. Nothing in the Editor-only pair exists there, so a reporter intended
for a device run must use the attribute-registered form.

## Supporting types

| Type | Role | Source |
|---|---|---|
| Test and result adaptors | The Editor-side view of one test and its outcome, including status and duration | [TestRunner.Api namespace](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEditor.TestTools.TestRunner.Api.html) |
| Assembly type, run state, test mode, test status | The enumerations a filter or a result is expressed in | [TestRunner.Api namespace](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEditor.TestTools.TestRunner.Api.html) |
| Test run settings | Applies temporary settings around a run and reverts them afterwards | [TestRunner.Api namespace](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEditor.TestTools.TestRunner.Api.html) |
