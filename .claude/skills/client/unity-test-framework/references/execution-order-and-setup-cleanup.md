# Execution Order, Setup & Cleanup

Source: [Setup and cleanup at build time](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/reference-setup-and-cleanup.html), [Actions outside tests](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/reference-actions-outside-tests.html), [`IPrebuildSetup`](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEngine.TestTools.IPrebuildSetup.html), [`IPostBuildCleanup`](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEngine.TestTools.IPostBuildCleanup.html), [`IOuterUnityTestAction`](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEngine.TestTools.IOuterUnityTestAction.html).

## Build-time setup/cleanup — `IPrebuildSetup` / `IPostBuildCleanup`

Two equivalent ways to hook pre-build/post-build actions:
1. Implement `IPrebuildSetup`/`IPostBuildCleanup` directly on the test class.
2. Apply `[PrebuildSetup("ClassName")]` / `[PostBuildCleanup("ClassName")]` (or the `Type`-overload constructor) at class, method, or **assembly** level, pointing at a class that implements the corresponding interface.

```csharp
[PrebuildSetup("MyTestSceneSetup")]
public class MyPlayModeTests
{
    // ...
}
```

- **`IPrebuildSetup.Setup()`** — actions to run as a pre-build step.
- **`IPostBuildCleanup.Cleanup()`** — actions to run as a post-build step.

**Execution order (verbatim):** "All setups run in a deterministic order one after another. The first to run are the setups defined with attributes. Then any test class implementing the interface runs, in alphabetical order inside their namespace, which is the same order tests run in."

**Cleanup timing (verbatim):** "Cleanup runs right away for a standalone test run, but only after related tests run in the Unity Editor." I.e. in-Editor, cleanup is deferred until after the whole related test run finishes; in a standalone Player run, it fires immediately.

Both setup and cleanup only run if the associated test/class is actually included in the current filtered run, and if multiple tests reference the same setup/cleanup class, it runs only **once**, not once per test.

- Attribute constructors: `PrebuildSetupAttribute(string)` / `PrebuildSetupAttribute(Type)`, `PostBuildCleanupAttribute(string)` / `PostBuildCleanupAttribute(Type)`. Valid `AttributeTargets`: `Assembly | Class | Method`.

## Actions outside tests — `IOuterUnityTestAction`, full execution order

`IOuterUnityTestAction` lets a **custom attribute** (one that inherits `NUnitAttribute` and implements this interface) inject `BeforeTest`/`AfterTest` hooks around a test, with the same yielding ability as `[UnityTest]`:

```csharp
public class MyOuterActionAttribute : NUnitAttribute, IOuterUnityTestAction
{
    public IEnumerator BeforeTest(ITest test)
    {
        yield return new EnterPlayMode();
    }

    public IEnumerator AfterTest(ITest test)
    {
        yield return new ExitPlayMode();
    }
}
```

Compatible with both `[Test]` and `[UnityTest]`, and can be combined with NUnit's own `ITestAction`.

### The full, ordered action pipeline (verbatim structure, 12 steps)

1. `IApplyToContext` attributes (NUnit-provided extensibility point — not part of this package's own API surface, referenced only conceptually here)
2. `IOuterUnityTestAction.BeforeTest`
3. `[UnitySetUp]` methods
4. `IWrapSetUpTearDown` attributes (NUnit)
5. `[SetUp]` attributes (NUnit)
6. Action attribute `BeforeTest` methods (NUnit `ITestAction`)
7. `IWrapTestMethod` attributes (NUnit)
8. **— test method executes —**
9. Action attribute `AfterTest` methods (NUnit `ITestAction`)
10. `[TearDown]` attributes (NUnit)
11. `[UnityTearDown]` methods
12. `IOuterUnityTestAction.AfterTest`

Standard NUnit inheritance rule still applies: `[SetUp]` runs base → derived; `[TearDown]` runs derived → base.

### Domain reload behavior — the sharpest edge case here

In Edit Mode tests, a yielded instruction can trigger a **domain reload** (entering/exiting Play Mode is the common case). What survives that reload differs by which kind of setup fired it:

> "When a domain reload happens, all non-Unity actions (such as `OneTimeSetup` and `Setup`) are rerun before the code that initiated the domain reload continues. Unity actions (such as `UnitySetup`) are not rerun. If the Unity action is the code that initiated the domain reload, then the rest of the code in the `UnitySetup` method runs after the domain reload."

In short: plain NUnit `[SetUp]`/`[OneTimeSetUp]` re-run after a domain reload; `[UnitySetUp]` does **not** re-run (its remaining code after the reload-triggering `yield` just resumes). Design any `[UnitySetUp]` that enters/exits Play Mode with this in mind — don't assume it restarts from the top after the reload the way a plain `[SetUp]` would.

## `[UnitySetUp]` / `[UnityTearDown]` recap

See [attributes-reference.md](attributes-reference.md) for the attribute signatures and a basic example. The distinguishing behavior versus plain `[SetUp]`/`[TearDown]` is: (a) the method must return `IEnumerator`/support yielding `IEditModeTestYieldInstruction`s, and (b) the domain-reload survival rule above.
