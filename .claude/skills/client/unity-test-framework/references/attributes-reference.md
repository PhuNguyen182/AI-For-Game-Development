# Custom Attributes Reference

Source: [Custom attributes](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/reference-custom-attributes.html) (manual table), cross-checked against the [`UnityEngine.TestTools`](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEngine.TestTools.html) and [`UnityEditor.TestTools`](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEditor.TestTools.html) API namespace pages.

## What's Unity-authored vs. plain NUnit

UTF layers a set of its own attributes on top of NUnit's own (`Test`, `TestCase`, `TestCaseSource`, `ValueSource`, `SetUp`, `TearDown`, `OneTimeSetUp`, `OneTimeTearDown`, `Ignore`, `Category`, `Timeout`). This project's manual/API pages only document Unity's additions — for NUnit's own attributes, consult [NUnit's documentation](https://docs.nunit.org/) directly rather than expecting Unity's site to re-explain them.

## The manual's attribute table (verbatim, 13 rows, alphabetical)

| Attribute | Namespace | Description (verbatim) |
|---|---|---|
| `ParameterizedIgnore` | `UnityEngine.TestTools` | A custom alternative to NUnit `Ignore` that allows ignoring tests based on parameters passed to the test method. |
| `PostBuildCleanup` | `UnityEngine.TestTools` | Make changes to Unity or the file system after building. |
| `PrebuildSetup` | `UnityEngine.TestTools` | Make changes to Unity or the file system before building. |
| `PreservedValues` | `UnityEngine.TestTools` | Like NUnit `Values`, this is used to provide literal arguments for an individual test parameter. |
| `RequirePlatformSupport` | `UnityEditor.TestTools` | Require Player build support for the specified platforms in order to run tests. |
| `RequiresPlayMode` | `UnityEngine.TestTools` | Can be applied to an assembly, fixture, or individual test to indicate that tests under its scope should (or should not) run in the Editor's Play Mode. |
| `TestMustExpectAllLogs` | `UnityEngine.TestTools` | Enforces that every log entry must be expected for a test to pass. |
| `TestPlayerBuildModifier` | `UnityEditor.TestTools` | Modify Player build options or split build and run. |
| `TestRunCallback` | `UnityEngine.TestRunner` | Assembly-level attribute used to subscribe a given type to updates on the test progress. |
| `UnityPlatform` | `UnityEngine.TestTools` | Define which platforms tests should run on. |
| `UnitySetUp` | `UnityEngine.TestTools` | Unity extension of NUnit `SetUp` to allow Unity yield instructions. |
| `UnityTearDown` | `UnityEngine.TestTools` | Unity extension of NUnit `TearDown` to allow Unity yield instructions. |
| `UnityTest` | `UnityEngine.TestTools` | Unity extension of NUnit `Test` to allow skipping frames and Unity yield instructions. |

**Important gap:** `ConditionalIgnoreAttribute` is a real, shipped attribute in `UnityEngine.TestTools` (see [assertions-logging-and-monobehaviour-testing.md](assertions-logging-and-monobehaviour-testing.md)) but it is **not listed in this manual table**. Don't treat the manual table as the exhaustive attribute list — cross-check the `UnityEngine.TestTools`/`UnityEditor.TestTools` namespace pages directly (linked in [root-links.md](root-links.md)) when auditing "every attribute this package offers."

## `[UnityTest]` — the core coroutine-test attribute

`UnityEngine.TestTools.UnityTestAttribute` — extends NUnit's `Test` to let a test method yield control back to the framework so background/async work can progress across frames. The test method returns `IEnumerator`.

- In **Play Mode**, a `[UnityTest]` method runs as an actual coroutine — ordinary coroutine yield instructions work (`WaitForFixedUpdate`, `WaitForSeconds`, `null` to skip a frame).
- In **Edit Mode**, it runs inside the `EditorApplication.update` loop; `yield return null` skips one editor update.

```csharp
[UnityTest]
public IEnumerator EditorUtility_WhenExecuted_ReturnsSuccess()
{
    var utility = RunEditorUtilityInTheBackground();
    while (utility.isRunning)
    {
        yield return null;
    }
    Assert.IsTrue(utility.isSuccess);
}
```

```csharp
[UnityTest]
public IEnumerator GameObject_WithRigidBody_WillBeAffectedByPhysics()
{
    var go = new GameObject();
    go.AddComponent<Rigidbody>();
    var originalPosition = go.transform.position.y;
    yield return new WaitForFixedUpdate();
    Assert.AreNotEqual(originalPosition, go.transform.position.y);
}
```

Known limits (see [getting-started-and-workflows.md](getting-started-and-workflows.md)): not supported on WSA; incompatible with `[Repeat]`; only `[ValueSource]` works for parameterization, not `[TestCase]`/`[TestCaseSource]` (see [async-coroutine-and-parameterized-tests.md](async-coroutine-and-parameterized-tests.md)).

## `[UnitySetUp]` / `[UnityTearDown]`

`UnityEngine.TestTools.UnitySetUpAttribute` / `UnityTearDownAttribute` — the yieldable equivalents of NUnit's `[SetUp]`/`[TearDown]`. The method must return `IEnumerator`.

```csharp
public class SetUpTearDownExample
{
    [UnitySetUp]
    public IEnumerator SetUp()
    {
        yield return new EnterPlayMode();
    }

    [Test]
    public void MyTest()
    {
        Debug.Log("This runs inside playmode");
    }

    [UnityTearDown]
    public IEnumerator TearDown()
    {
        yield return new ExitPlayMode();
    }
}
```

See [execution-order-and-setup-cleanup.md](execution-order-and-setup-cleanup.md) for exactly where these fire relative to plain NUnit `SetUp`/`TearDown` and `IOuterUnityTestAction`, and for the domain-reload rule that specifically affects `UnitySetUp`.

## `[RequiresPlayMode]`

`UnityEngine.TestTools.RequiresPlayModeAttribute` — see [getting-started-and-workflows.md](getting-started-and-workflows.md)'s "Edit Mode vs. Play Mode" section for the full decision table. Can target an assembly, a fixture, or a single test.

## `[UnityPlatform]` / `[RequirePlatformSupport]` / `[TestPlayerBuildModifier]`

Covered in full in [platform-build-and-command-line.md](platform-build-and-command-line.md).

## `[PrebuildSetup]` / `[PostBuildCleanup]`

Covered in full in [execution-order-and-setup-cleanup.md](execution-order-and-setup-cleanup.md).

## `[TestMustExpectAllLogs]` / `[PreservedValues]` / `[ConditionalIgnore]` / `[ParameterizedIgnore]`

Covered in [assertions-logging-and-monobehaviour-testing.md](assertions-logging-and-monobehaviour-testing.md) and [async-coroutine-and-parameterized-tests.md](async-coroutine-and-parameterized-tests.md) respectively.

## `[TestRunCallback]`

`UnityEngine.TestRunner.TestRunCallbackAttribute` — assembly-level, subscribes a type implementing `ITestRunCallback` to raw test-progress notifications. Covered in [scripting-api-test-runner-api.md](scripting-api-test-runner-api.md).
