# Assertions, Logging and MonoBehaviour Testing — what to assert and how

Sources: [LogAssert](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEngine.TestTools.LogAssert.html), [TestMustExpectAllLogsAttribute](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEngine.TestTools.TestMustExpectAllLogsAttribute.html), [Utils](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEngine.TestTools.Utils.html), [Constraints](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEngine.TestTools.Constraints.html), [MonoBehaviourTest](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEngine.TestTools.MonoBehaviourTest-1.html), [IMonoBehaviourTest](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEngine.TestTools.IMonoBehaviourTest.html).
Covers: SKILL.md §4 — **"Expect a log before the code under test emits it"**, **"Compare Unity value types through the framework's own comparers"**, **"Gate a no-allocation claim with an allocation constraint rather than a review note"**.

The assertion surface this package adds over NUnit's: log expectations,
tolerance-aware equality for Unity types, an allocation constraint, and a
wrapper for MonoBehaviours whose completion is a condition rather than a
frame count.

## Log expectations

| Member | Effect | Source |
|---|---|---|
| Expect a log | Registers that a matching entry is required; the entry is matched at frame end, so the call must come before the code that logs | [LogAssert](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEngine.TestTools.LogAssert.html) |
| Ordering | Several expectations are matched in the order the entries were logged, so registering them out of order fails a test whose behaviour is correct | [LogAssert](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEngine.TestTools.LogAssert.html) |
| Unexpected entries | An error-level log the test did not expect fails it on its own, which is what makes a silent error impossible to pass by accident | [LogAssert](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEngine.TestTools.LogAssert.html) |
| No unexpected received | Asserts that nothing further was logged at the point it is called, for a test whose contract is silence | [LogAssert](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEngine.TestTools.LogAssert.html) |
| Must expect all logs | Raises the bar for the whole test: every entry at any level must be expected, not only errors | [TestMustExpectAllLogsAttribute](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEngine.TestTools.TestMustExpectAllLogsAttribute.html) |

## Equality for Unity value types

| Comparer | Why the default is not enough | Source |
|---|---|---|
| Float comparer | Floating-point results rarely match exactly, so the default equality fails on precision rather than on behaviour | [Utils](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEngine.TestTools.Utils.html) |
| Vector comparers, two through four components | Per-component tolerance, so an accumulated transform result compares meaningfully instead of bit-exactly | [Utils](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEngine.TestTools.Utils.html) |
| Quaternion comparer | Handles the tolerance a rotation needs, which a component-wise comparison of the same values does not | [Utils](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEngine.TestTools.Utils.html) |
| Colour comparer | Compares channel values within a tolerance, for results that pass through a colour-space conversion | [Utils](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEngine.TestTools.Utils.html) |

**Critical caveat**: a hand-rolled epsilon check reimplements these comparers
one assertion at a time, and each copy carries its own tolerance. Use the
supplied comparer so the tolerance is one decision, not many.

## Allocation constraint

| Subject | What it decides | Source |
|---|---|---|
| Allocating-GC-memory constraint | Asserts whether a delegate allocates managed memory, turning a hot-path rule into a regression gate that a later refactor cannot quietly break | [Constraints](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEngine.TestTools.Constraints.html) |
| Scope | It is a pass-or-fail correctness gate on one call, not a measurement — sizing and attribution belong to `unity-profiler-diagnostics` | [Constraints](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEngine.TestTools.Constraints.html) |

## MonoBehaviour condition tests

| Subject | What it decides | Source |
|---|---|---|
| The interface | The component reports when it considers itself finished, so the test waits on a condition rather than a guessed number of frames | [IMonoBehaviourTest](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEngine.TestTools.IMonoBehaviourTest.html) |
| The generic wrapper | Instantiates the component, runs until it reports completion, and cleans up — which is what makes the pattern shorter than an equivalent coroutine test | [MonoBehaviourTest](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEngine.TestTools.MonoBehaviourTest-1.html) |
| When not to use it | An assertion expressible directly in a coroutine does not need the wrapper; the wrapper earns its place when completion is genuinely a condition | [MonoBehaviourTest](https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/api/UnityEngine.TestTools.MonoBehaviourTest-1.html) |
