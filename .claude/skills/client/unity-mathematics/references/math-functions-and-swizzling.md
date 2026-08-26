# The math Class & Swizzling — Elementary Functions and Component Rearrangement

Source: [math](https://docs.unity3d.com/Packages/com.unity.mathematics@1.3/api/Unity.Mathematics.math.html), [float3](https://docs.unity3d.com/Packages/com.unity.mathematics@1.3/api/Unity.Mathematics.float3.html).
Covers: SKILL.md §4 — **"Use swizzling for readable component rearrangement"**, **"Use the static `math` class for every elementary function"**.

The function surface that replaces `Mathf`/`System.Math` inside `Game.Core.*`
and Burst-compiled code, and the swizzle accessors that rearrange components
without building a new vector by hand. Why `Mathf` is disallowed on that side
of the boundary is
[shared-core-and-burst-compatibility.md](shared-core-and-burst-compatibility.md).

## Commonly used math members

| Member | Effect | Use when | Source |
|---|---|---|---|
| `math.normalize` | Returns the unit-length vector | A direction is needed, not a displacement | [math](https://docs.unity3d.com/Packages/com.unity.mathematics@1.3/api/Unity.Mathematics.math.html) |
| `math.dot` / `math.cross` | Scalar and vector products | Angle tests, projection, or a perpendicular axis | [math](https://docs.unity3d.com/Packages/com.unity.mathematics@1.3/api/Unity.Mathematics.math.html) |
| `math.distance` | True Euclidean distance — computes a square root | The absolute distance value itself is used | [math](https://docs.unity3d.com/Packages/com.unity.mathematics@1.3/api/Unity.Mathematics.math.html) |
| `math.distancesq` | Squared distance — no square root | Only comparing against a threshold; pre-square the threshold | [math](https://docs.unity3d.com/Packages/com.unity.mathematics@1.3/api/Unity.Mathematics.math.html) |
| `math.saturate` | Clamps to `[0, 1]` | Replacing `Mathf.Clamp01` | [math](https://docs.unity3d.com/Packages/com.unity.mathematics@1.3/api/Unity.Mathematics.math.html) |
| `math.clamp` / `math.lerp` | Bounded range and linear interpolation | Replacing `Mathf.Clamp`/`Mathf.Lerp` | [math](https://docs.unity3d.com/Packages/com.unity.mathematics@1.3/api/Unity.Mathematics.math.html) |
| `math.sin` / `math.cos` / `math.sqrt` | Transcendental and root functions | Replacing `Mathf`/`System.Math` equivalents | [math](https://docs.unity3d.com/Packages/com.unity.mathematics@1.3/api/Unity.Mathematics.math.html) |

**Critical caveat**: `math` and `Mathf`/`System.Math` are not guaranteed to
agree bit-for-bit on the same named function — a precision-sensitive
comparison must be verified, not assumed, per SKILL.md's verification step.

## Swizzling

| Property | What it decides | Source |
|---|---|---|
| Result width follows the name | `v.xy` yields a `float2`, `v.xyz` a `float3`, `v.xxyy` a `float4` — the component count named is the type returned | [float3](https://docs.unity3d.com/Packages/com.unity.mathematics@1.3/api/Unity.Mathematics.float3.html) |
| Repetition and reordering are legal | `v.zyx` reverses, `v.xxyy` duplicates — any combination of the type's component letters | [float3](https://docs.unity3d.com/Packages/com.unity.mathematics@1.3/api/Unity.Mathematics.float3.html) |
| Available on every vector type | `float2`/`float3`/`float4` and their `int`/`bool`/`double` variants alike | [float3](https://docs.unity3d.com/Packages/com.unity.mathematics@1.3/api/Unity.Mathematics.float3.html) |
| Read/write accessors, not copies of a field | Generated properties, so no allocation and no manual construction | [float3](https://docs.unity3d.com/Packages/com.unity.mathematics@1.3/api/Unity.Mathematics.float3.html) |
| Documented per combination | Each swizzle is its own Scripting API property (e.g. `float3.yzxy`) rather than one consolidated page — consult the type's own API page for the full list, see [vector-and-matrix-types.md](vector-and-matrix-types.md) | [float3](https://docs.unity3d.com/Packages/com.unity.mathematics@1.3/api/Unity.Mathematics.float3.html) |
