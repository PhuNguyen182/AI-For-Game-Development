# Assertions, logs, allocations, MonoBehaviour tests

## `LogAssert`
- `LogAssert.Expect` must be called before the code logs; matching happens at frame end.
- Multiple expectations match in logged order — registering out of order fails correct behaviour.
- An unexpected error-level log fails the test by itself.
- `LogAssert.NoUnexpectedReceived()` asserts silence at that point.
- `[TestMustExpectAllLogs]` requires every entry at any level to be expected.

## Value comparers (`UnityEngine.TestTools.Utils`)
Use `FloatEqualityComparer`, `Vector2/3/4EqualityComparer`, `QuaternionEqualityComparer`, `ColorEqualityComparer`. Default equality fails on precision, and a hand-rolled epsilon duplicates the tolerance per assertion.

## Allocation constraint
`Is.Not.AllocatingGCMemory()` (`UnityEngine.TestTools.Constraints`) asserts one delegate allocates no managed memory. It is a pass/fail gate, not a measurement (`unity-profiler-diagnostics`).

## `MonoBehaviourTest<T>`
`T : MonoBehaviour, IMonoBehaviourTest` reports `IsTestFinished`; the wrapper instantiates it, waits on the condition and cleans up. Use it when completion is a condition; an assertion expressible directly in a coroutine does not need it.
