# Scripting API — Programmatic Test Running (`TestRunnerApi`)

Source: [Namespace `UnityEditor.TestTools.TestRunner.Api`](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEditor.TestTools.TestRunner.Api.html), [`TestRunnerApi`](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEditor.TestTools.TestRunner.Api.TestRunnerApi.html), [`Filter`](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEditor.TestTools.TestRunner.Api.Filter.html), [`ExecutionSettings`](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEditor.TestTools.TestRunner.Api.ExecutionSettings.html), [`ICallbacks`](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEditor.TestTools.TestRunner.Api.ICallbacks.html), [`IErrorCallbacks`](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEditor.TestTools.TestRunner.Api.IErrorCallbacks.html), [Namespace `UnityEngine.TestRunner`](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEngine.TestRunner.html).

This is an **Editor-only** API (`UnityEditor.*`) for retrieving and running tests **programmatically** from your own Editor tooling/package code, instead of driving the Test Runner window by hand. All types below live in namespace `UnityEditor.TestTools.TestRunner.Api` unless stated otherwise.

## `TestRunnerApi` — the entry point

A `ScriptableObject`. Create it with:
```csharp
var testRunnerApi = ScriptableObject.CreateInstance<TestRunnerApi>();
```

**Methods:**
| Method | Purpose |
|---|---|
| `Execute(ExecutionSettings)` | Starts a test run (instance method). |
| `ExecuteTestRun(ExecutionSettings)` | Starts a test run (**static**, preferred — see remarks below). |
| `RetrieveTestList(TestMode, Action<ITestAdaptor>)` | Retrieves the full test tree for a given mode. |
| `RetrieveTestTree(ExecutionSettings, Action<ITestAdaptor>)` | Retrieves the tests matching a given `ExecutionSettings` filter set. |
| `RegisterCallbacks<T>(T, int)` | Registers an `ICallbacks` instance (instance method). |
| `RegisterTestCallback<T>(T, int)` | Registers an `ICallbacks` instance (**static**, preferred). |
| `UnregisterCallbacks<T>(T)` / `UnregisterTestCallback<T>(T)` | Unregister counterparts. |
| `RegisterCustomRunner(CustomRunnerBase)` / `UnregisterCustomRunner(CustomRunnerBase)` | Register/unregister a `CustomRunnerBase` implementation. |
| `CancelTestRun(string guid)` | Cancels the run with the given guid. |
| `CancelAllTestRuns()` | Cancels all running test runs — **currently Edit Mode-only**. |
| `IsRunActive(string guid)` / `IsAnyRunActive()` | Query run status. |
| `GetActiveRunGuids()` | Guids of all currently active runs. |
| `GetExecutionSettings(string guid)` | The `ExecutionSettings` for a run by guid. |
| `GetCustomRunnerNames()` | Names of currently registered custom runners. |
| `SaveResultToFile(ITestResultAdaptor, string path)` | Saves a result to a file. |

**Remarks (important):**
- "Non-static methods in this class will become obsolete in future versions — use the static methods (e.g. `RegisterTestCallback`, `ExecuteTestRun`) rather than their non-static equivalents." Prefer the static forms in any new code against this API, per `coding-principles.md`'s Obsolete APIs rule (don't build new tooling against a member already flagged for future obsolescence when a current alternative exists).
- "Registered callbacks are not persisted across domain reloads — re-register the callback after a domain reload, usually via `[InitializeOnLoad]`."
- "Listeners receive callbacks from **all** test runs, regardless of which `TestRunnerApi` instance registered them" — a callback isn't scoped to the instance that registered it.

## `Filter` — which tests to run

```csharp
public class Filter : ISerializationCallbackReceiver
```

| Field | Purpose |
|---|---|
| `testMode` | `TestMode` flag — Edit Mode / Play Mode. |
| `assemblyNames` | Assembly names (no `.dll` extension) to include. |
| `assemblyType` | `AssemblyType` flag — editor-only vs. platform-supporting. |
| `categoryNames` | Category names to include. |
| `groupNames` | Regex-capable names matching fixtures/namespaces. |
| `testNames` | Full names `"FixtureName.TestName"`, optionally with parameterized-test arguments. |
| `requiresPlayMode` | Nullable bool — filter by `[RequiresPlayMode]` tagging. |
| `targetPlatform` | `BuildTarget?` — `null` targets the Editor. |

## `ExecutionSettings` — how to run them

```csharp
public class ExecutionSettings // [Serializable], ISerializationCallbackReceiver
```

**Constructor:** `ExecutionSettings(params Filter[] filters)`.

| Member | Purpose |
|---|---|
| `filters` | The `Filter[]` selecting which tests to run. |
| `targetPlatform` | `BuildTarget?` — `null` runs in the Editor. |
| `runSynchronously` | Edit-Mode-only; excludes multi-frame tests. |
| `playerHeartbeatTimeout` | Seconds to wait for Player heartbeats (default 10 minutes). |
| `customRunnerName` | Name of a registered `CustomRunnerBase` to use instead of the default runner. |
| `overloadTestRunSettings` | An `ITestRunSettings` applying/reverting global Editor settings around the run. |
| `IsBuildOnly` (property) | Whether this run only builds the Player without executing tests. |
| `playerSavePath` (property) | Where the built Player is saved. |

## Callbacks — two distinct interfaces, don't conflate them

There are **two separate callback surfaces** in this package, in different namespaces, using different test-node types:

1. **`UnityEditor.TestTools.TestRunner.Api.ICallbacks`** (Editor-only) — uses `ITestAdaptor`/`ITestResultAdaptor` (Editor-side wrappers around NUnit's `ITest`/`ITestResult`):
   ```csharp
   public interface ICallbacks
   {
       void RunStarted(ITestAdaptor testsToRun);
       void RunFinished(ITestResultAdaptor result);
       void TestStarted(ITestAdaptor test);
       void TestFinished(ITestResultAdaptor result);
   }
   ```
   Extended by **`IErrorCallbacks : ICallbacks`**, adding `void OnError(string message)` — invoked on a build failure or an `IPrebuildSetup` failure. Register via `TestRunnerApi.RegisterTestCallback`/`RegisterCallbacks`.

2. **`UnityEngine.TestRunner.ITestRunCallback`** (Editor **and** Player) — uses raw NUnit `ITest`/`ITestResult` directly:
   ```csharp
   public interface ITestRunCallback
   {
       void RunStarted(ITest testsToRun);
       void RunFinished(ITestResult result);
       void TestStarted(ITest test);
       void TestFinished(ITestResult result);
   }
   ```
   Registered via the assembly-level **`[TestRunCallback(typeof(YourListenerType))]`** attribute, not through `TestRunnerApi`:
   ```csharp
   using NUnit.Framework.Interfaces;
   using UnityEngine;
   using UnityEngine.TestRunner;

   [assembly: TestRunCallback(typeof(TestListener))]

   public class TestListener : ITestRunCallback
   {
       public void RunStarted(ITest testsToRun) { }

       public void RunFinished(ITestResult testResults)
       {
           Debug.Log($"Run finished with result {testResults.ResultState}.");
       }

       public void TestStarted(ITest test) { }

       public void TestFinished(ITestResult result) { }
   }
   ```
   Key property (verbatim): "The `TestRunCallback` does not need any references to the `UnityEditor` namespace and can run in standalone Players on the Player side." Use this one when the listener genuinely needs to run inside a built Player (e.g. reporting results from a device-run test back over the network) — use `ICallbacks`/`IErrorCallbacks` for Editor-side tooling that can depend on `UnityEditor`.

## Other supporting types

| Type | Kind | Purpose |
|---|---|---|
| `ITestAdaptor` | interface | A node in the Editor-side test tree, wrapping NUnit's `ITest`. |
| `ITestResultAdaptor` | interface | The result for a tree node, wrapping NUnit's `ITestResult`. |
| `ITestRunSettings` | interface | Applies global Editor settings right before building a test Player, then reverts them afterward. |
| `AssemblyType` | enum | `EditorOnly` / `EditorAndPlatforms` flags. |
| `RunState` | enum | Whether a given test can currently be executed. |
| `TestMode` | enum | Edit Mode / Play Mode flags. |
| `TestStatus` | enum | Passed/Failed/Skipped/etc. result status. |
| `CustomRunnerBase` | class | Base type for a custom test runner registered with `TestRunnerApi.RegisterCustomRunner`. |
| `RunnerNotFoundException` | exception | Thrown when a runner with a given guid can't be found. |

## When to reach for this API vs. the Test Runner window

Use `TestRunnerApi` when a task genuinely needs to run/enumerate tests from your own Editor tooling code — a custom CI dashboard inside the Editor, a pre-commit hook script, an Editor window aggregating results across several filters. For routine day-to-day test authoring/running, the Test Runner window and the command-line flags in [platform-build-and-command-line.md](platform-build-and-command-line.md) are simpler (KISS) — don't reach for `TestRunnerApi` just to run "all tests" when `-runTests -batchmode` already does that.
