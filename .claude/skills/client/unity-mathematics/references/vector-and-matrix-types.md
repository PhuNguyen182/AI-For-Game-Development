# Vector & Matrix Types — floatN, quaternion, float3x3/float4x4

Source: [Unity Mathematics](https://docs.unity3d.com/Packages/com.unity.mathematics@1.3/manual/index.html), [Getting started](https://docs.unity3d.com/Packages/com.unity.mathematics@1.3/manual/getting-started.html), [float3](https://docs.unity3d.com/Packages/com.unity.mathematics@1.3/api/Unity.Mathematics.float3.html), [float4](https://docs.unity3d.com/Packages/com.unity.mathematics@1.3/api/Unity.Mathematics.float4.html), [quaternion](https://docs.unity3d.com/Packages/com.unity.mathematics@1.3/api/Unity.Mathematics.quaternion.html), [float4x4](https://docs.unity3d.com/Packages/com.unity.mathematics@1.3/api/Unity.Mathematics.float4x4.html).
Covers: SKILL.md §4 — **"Pick the vector width that matches the actual dimensionality"**, **"Use `quaternion` for all Shared Core/Burst/ECS rotation data"**, **"Use `float3x3`/`float4x4` with the library's own factory methods"**.

The type surface and the factory methods that construct each one correctly.
Why these types belong in Shared Core at all is
[shared-core-and-burst-compatibility.md](shared-core-and-burst-compatibility.md);
the functions operating on them are
[math-functions-and-swizzling.md](math-functions-and-swizzling.md).

## Package facts

| Fact | What it decides | Source |
|---|---|---|
| Shader-like syntax by design | Vector/matrix types and elementary functions mirror shader conventions, so the same expression reads the same in both places | [Unity Mathematics](https://docs.unity3d.com/Packages/com.unity.mathematics@1.3/manual/index.html) |
| Built into the Editor from Unity 6.5 | No separate package installation step is needed on 6.5+ | [Unity Mathematics](https://docs.unity3d.com/Packages/com.unity.mathematics@1.3/manual/index.html) |
| `using Unity.Mathematics;` | The single import that exposes the whole library | [Getting started](https://docs.unity3d.com/Packages/com.unity.mathematics@1.3/manual/getting-started.html) |
| Lowercase type names are deliberate | `float3`/`quaternion` signal "Burst-optimized and shader-portable" — Unity's convention, not a project naming violation to be corrected | [Getting started](https://docs.unity3d.com/Packages/com.unity.mathematics@1.3/manual/getting-started.html) |
| Burst treats them as first-class | Burst extends C#'s native type set with these vectors/matrices/quaternions and optimizes them directly | [Getting started](https://docs.unity3d.com/Packages/com.unity.mathematics@1.3/manual/getting-started.html) |

## Choosing a type

| Type | Effect | Use when | Source |
|---|---|---|---|
| `float3` | 3-component float vector; constructors, indexer, operators, `Equals`/`GetHashCode`/`ToString` | The data is genuinely 3D — position, direction, scale | [float3](https://docs.unity3d.com/Packages/com.unity.mathematics@1.3/api/Unity.Mathematics.float3.html) |
| `float2` / `float4` | Same shape at 2 and 4 components | 2D/planar data, or a real 4-component value: homogeneous coordinate, RGBA colour | [float4](https://docs.unity3d.com/Packages/com.unity.mathematics@1.3/api/Unity.Mathematics.float4.html) |
| `int`/`bool`/`double` variants | `int3`, `bool4`, `double2` and siblings follow the identical shape | Integer indices, per-lane masks, or double precision are required | [float3](https://docs.unity3d.com/Packages/com.unity.mathematics@1.3/api/Unity.Mathematics.float3.html) |
| `quaternion` | The rotation type, with equality and formatting support | Any rotation outside a MonoBehaviour's own `Transform` access | [quaternion](https://docs.unity3d.com/Packages/com.unity.mathematics@1.3/api/Unity.Mathematics.quaternion.html) |
| `float4x4` | 4x4 matrix with transform methods and composition operators | Full transform composition including translation | [float4x4](https://docs.unity3d.com/Packages/com.unity.mathematics@1.3/api/Unity.Mathematics.float4x4.html) |
| `float3x3` | Same pattern, rotation and scale only | No translation component is needed — smaller and cheaper | [float4x4](https://docs.unity3d.com/Packages/com.unity.mathematics@1.3/api/Unity.Mathematics.float4x4.html) |

## Factory methods — construct through these, not field-by-field

| Factory | Effect | Source |
|---|---|---|
| `quaternion.identity` | The no-rotation value | [quaternion](https://docs.unity3d.com/Packages/com.unity.mathematics@1.3/api/Unity.Mathematics.quaternion.html) |
| `quaternion.AxisAngle` | Rotation about an arbitrary axis by an angle | [quaternion](https://docs.unity3d.com/Packages/com.unity.mathematics@1.3/api/Unity.Mathematics.quaternion.html) |
| `quaternion.Euler` | Rotation from Euler angles | [quaternion](https://docs.unity3d.com/Packages/com.unity.mathematics@1.3/api/Unity.Mathematics.quaternion.html) |
| `quaternion.LookRotation` | Rotation aligning forward to a direction | [quaternion](https://docs.unity3d.com/Packages/com.unity.mathematics@1.3/api/Unity.Mathematics.quaternion.html) |
| `float4x4.TRS` | Translation/rotation/scale composed in one call | [float4x4](https://docs.unity3d.com/Packages/com.unity.mathematics@1.3/api/Unity.Mathematics.float4x4.html) |
| `float4x4.LookAt` | A look-at transform matrix | [float4x4](https://docs.unity3d.com/Packages/com.unity.mathematics@1.3/api/Unity.Mathematics.float4x4.html) |

**Critical caveat**: constructing a `quaternion` field-by-field produces a
value that is not normalized and not reported as invalid — every rotation
built outside these factories is a silent correctness risk.
