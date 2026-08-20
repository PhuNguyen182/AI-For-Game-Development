# Assertions, Log Expectations & MonoBehaviour Testing

Source: [`LogAssert`](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEngine.TestTools.LogAssert.html), [`Constraints`](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEngine.TestTools.Constraints.html), [`Utils`](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEngine.TestTools.Utils.html), [`MonoBehaviourTest<T>`](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEngine.TestTools.MonoBehaviourTest-1.html), [`IMonoBehaviourTest`](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEngine.TestTools.IMonoBehaviourTest.html), [`ConditionalIgnoreAttribute`](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEngine.TestTools.ConditionalIgnoreAttribute.html), [`TestMustExpectAllLogsAttribute`](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEngine.TestTools.TestMustExpectAllLogsAttribute.html), [`PreservedValuesAttribute`](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEngine.TestTools.PreservedValuesAttribute.html).

There is **no separate "assertions" manual page** in this package version (unlike 1.x, whose `reference-custom-assertion.html` 404s here) — `utf-features.html` links straight to the `LogAssert` API page, which is the authoritative source below. Plain `Assert.*`/`Assert.That` assertions are NUnit's own; this page covers only Unity's additions on top.

## `LogAssert` — expecting Unity log messages

`UnityEngine.TestTools.LogAssert` (static class): "LogAssert lets you expect Unity log messages that would otherwise cause the test to fail." Without it, `Debug.LogError`/`Debug.LogException`/a failed `Debug.Assert` inside the code under test would fail the test outright.

- **`LogAssert.Expect(LogType logType, string message)`** — declares that a log of the given type and exact text is expected; the test fails if that message never actually appears.
- **`LogAssert.Expect(LogType logType, Regex pattern)`** — same, but matched via regex instead of an exact string.
- **Ordering rule:** if multiple `Expect` calls are made, the actual logs must appear in that same sequential order.
- **Usage rule (verbatim guidance):** call `LogAssert.Expect` **before** running the code under test — the framework's check for expected logs happens at the end of each frame, not synchronously at the call site.
- **`LogAssert.NoUnexpectedReceived()`** — fails the test if any log message was received that wasn't explicitly `Expect`-ed. Prefer `[TestMustExpectAllLogs]` (below) over sprinkling this call everywhere when the requirement is "every log across many tests must be expected."
- **`LogAssert.ignoreFailingMessages`** (bool, default `false`) — set `true` to stop unexpected error-level logs from failing the test (use sparingly — it silences a real signal).

```csharp
[Test]
public void DamageCalculation_WithInvalidTarget_LogsWarning()
{
    LogAssert.Expect(LogType.Warning, "Target is not damageable.");
    DamageResolver.Resolve(attacker, invalidTarget);
}
```

## `[TestMustExpectAllLogs]`

`UnityEngine.TestTools.TestMustExpectAllLogsAttribute` — "Enforces that every log entry must be expected for a test to pass." Apply this when a test (or fixture) should fail on *any* unlogged/unexpected message, without having to call `LogAssert.NoUnexpectedReceived()` manually in every test method.

## `[ConditionalIgnore]`

`UnityEngine.TestTools.ConditionalIgnoreAttribute` — an alternative to NUnit's plain `[Ignore]` that skips a test only when a named condition evaluates true. The condition is checked during `OnLoad`, keyed by a string ID you register ahead of time.

- Constructor: `ConditionalIgnoreAttribute(string conditionKey, string reason)`.
- Static registration: `ConditionalIgnoreAttribute.AddConditionalIgnoreMapping(string conditionKey, bool shouldIgnore)` — call this (typically from an `[InitializeOnLoad]` static hook) before the affected tests run.
- Implements NUnit's `IApplyToTest` via `ApplyToTest(Test)` to perform the actual skip.

```csharp
[InitializeOnLoad]
public static class ConditionalIgnoreSetup
{
    static ConditionalIgnoreSetup()
    {
        ConditionalIgnoreAttribute.AddConditionalIgnoreMapping(
            "IgnoreOnMobile", Application.isMobilePlatform);
    }
}

[ConditionalIgnore("IgnoreOnMobile", "Not relevant on mobile targets.")]
[Test]
public void DesktopOnlyBehavior_Test() { /* ... */ }
```

**Reminder:** `ConditionalIgnoreAttribute` is real and shipped, but is missing from the manual's `reference-custom-attributes.html` table (see [attributes-reference.md](attributes-reference.md)) — don't conclude it doesn't exist just because that table omits it.

## `[PreservedValues]`

`UnityEngine.TestTools.PreservedValuesAttribute` — like NUnit's `[Values]`, supplies literal arguments for one test parameter, but marked so the values survive aggressive managed-code stripping (relevant on IL2CPP builds with a high stripping level, where an un-preserved literal/reflection-discovered value could otherwise be stripped).

## Custom equality comparers — `UnityEngine.TestTools.Utils`

Provides `Assert.That`-compatible equality comparers for common Unity math/color types: `Color`, `Float` (an epsilon-based float comparer), `Quaternion`, `Vector2`, `Vector3`, `Vector4`. Use these instead of exact `==`/`Assert.AreEqual` on floating-point-derived types, since floating-point Vector/Quaternion/Color comparisons need a tolerance, not bit-exact equality.

## Custom constraints — `UnityEngine.TestTools.Constraints`

Extends NUnit's `Assert.That(...)` constraint model with Unity-specific constraints (e.g. an allocation-checking constraint used to assert a piece of code performs zero GC allocations — directly useful for enforcing `performance-and-algorithms.md`'s no-per-frame-allocation rule with an actual automated test rather than a manual Profiler check). Confirm the exact constraint names/usage against the live API page before depending on a specific one, since this class's member list wasn't independently re-verified line-by-line during this skill's research pass.

## `MonoBehaviourTest<T>` / `IMonoBehaviourTest` — testing a MonoBehaviour via coroutine

- **`IMonoBehaviourTest`** — implement this on the MonoBehaviour under test; it exposes a single member, `bool IsTestFinished { get; }`, that the framework polls to know when the behaviour's self-contained test logic is done.
- **`MonoBehaviourTest<T>`** (where `T : MonoBehaviour, IMonoBehaviourTest`) — a `CustomYieldInstruction` that instantiates `T`, waits until `IsTestFinished` is true, and exposes `component` (the created instance) and `gameObject` (its container).

```csharp
public class MySelfTestingBehaviour : MonoBehaviour, IMonoBehaviourTest
{
    private int _frameCount;

    public bool IsTestFinished => _frameCount > 2;

    private void Update()
    {
        _frameCount++;
    }
}

public class MonoBehaviourTests
{
    [UnityTest]
    public IEnumerator MySelfTestingBehaviour_RunsForAFewFrames_ThenFinishes()
    {
        yield return new MonoBehaviourTest<MySelfTestingBehaviour>();
    }
}
```

Reach for `MonoBehaviourTest<T>` when the thing under test is genuinely a self-contained MonoBehaviour whose completion condition is naturally expressed as "keep running until `IsTestFinished`" — for anything that can be tested by driving a `[UnityTest]` coroutine directly with explicit `Assert` calls, prefer the plain coroutine test (simpler, per KISS in `coding-principles.md`) over wrapping it in `MonoBehaviourTest<T>`.
