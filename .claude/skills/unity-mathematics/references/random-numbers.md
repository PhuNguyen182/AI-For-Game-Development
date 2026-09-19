# Random Numbers — Unity.Mathematics.Random

Source: [Random numbers](https://docs.unity3d.com/Packages/com.unity.mathematics@1.3/manual/random-numbers.html), [Random](https://docs.unity3d.com/Packages/com.unity.mathematics@1.3/api/Unity.Mathematics.Random.html).
Covers: SKILL.md §4 — **"For any Shared Core RNG need, use `Unity.Mathematics.Random` with an explicit, injected, nonzero seed"**.

The RNG whose state is entirely caller-managed, which is what makes it the
answer to `coding-principles.md`'s requirement for a seeded, injectable RNG in
Shared Core where `UnityEngine.Random`'s implicit global state is disallowed.

## State model

| Property | What it decides | Source |
|---|---|---|
| Caller creates and manages the state | The sequence is reproducible because nothing global advances it behind your back | [Random numbers](https://docs.unity3d.com/Packages/com.unity.mathematics@1.3/manual/random-numbers.html) |
| Independent instances do not interfere | Per-thread or per-context instances stay uncorrelated, which is what makes it safe in parallel code | [Random numbers](https://docs.unity3d.com/Packages/com.unity.mathematics@1.3/manual/random-numbers.html) |
| 32 bits of state, xorshift-based | Small enough to embed cheaply inside a component or struct | [Random](https://docs.unity3d.com/Packages/com.unity.mathematics@1.3/api/Unity.Mathematics.Random.html) |
| Avoids integer multiplication in its core ops | Vectorizes well on limited SIMD instruction sets | [Random](https://docs.unity3d.com/Packages/com.unity.mathematics@1.3/api/Unity.Mathematics.Random.html) |
| It is a mutable struct | Advancing state requires passing by `ref`; a by-value copy silently replays the same sequence | [Random](https://docs.unity3d.com/Packages/com.unity.mathematics@1.3/api/Unity.Mathematics.Random.html) |

## Construction and use

| Call | Effect | Use when | Source |
|---|---|---|---|
| `new Random(uint seed)` | Constructs with an explicit seed | Normal construction — the seed must be non-zero | [Random](https://docs.unity3d.com/Packages/com.unity.mathematics@1.3/api/Unity.Mathematics.Random.html) |
| `InitState(uint seed = 1851936439U)` | Resets an existing instance's state | Reusing one instance across runs or rounds | [Random](https://docs.unity3d.com/Packages/com.unity.mathematics@1.3/api/Unity.Mathematics.Random.html) |
| `NextFloat()` | Returns a value in `[0, 1)` | The default uniform draw | [Random numbers](https://docs.unity3d.com/Packages/com.unity.mathematics@1.3/manual/random-numbers.html) |
| `NextFloat(min, max)` | Returns a value in the given range, e.g. `NextFloat(-5.0f, 5.0f)` | A custom range is needed | [Random numbers](https://docs.unity3d.com/Packages/com.unity.mathematics@1.3/manual/random-numbers.html) |

**Critical caveat**: a zero seed is invalid, and deriving a seed from
wall-clock time defeats the determinism the type exists to provide. Both
produce code that runs normally and diverges between client and server.
