# Vector & Matrix Types

Covers SKILL.md steps 2, 5, 6 (picking the right vector width, rotation type, and matrix type).

## Manual
- [Unity Mathematics](https://docs.unity3d.com/Packages/com.unity.mathematics@1.3/manual/index.html) — a C# math library providing vector/matrix types (`floatN`, `quaternion`, `float3x3`, `float4x4`) and elementary functions (`min`, `max`, `fabs`, `sin`, `cos`, `sqrt`, `normalize`, `dot`, `cross`) with a shader-like syntax. From Unity 6.5 onward the package is built into the Editor and needs no separate installation.
- [Getting started](https://docs.unity3d.com/Packages/com.unity.mathematics@1.3/manual/getting-started.html) — `using Unity.Mathematics;` to access the library. The Burst compiler extends C#'s native type set with vectors/matrices/quaternions as first-class constructs it can optimize. Built-in type names are deliberately all-lowercase (`float3`, `quaternion`) to signal both "Burst-optimized" and "shader-portable" — this is Unity's own naming convention for this library, not a project-code naming violation.

## API
- [float3](https://docs.unity3d.com/Packages/com.unity.mathematics@1.3/api/Unity.Mathematics.float3.html) — a 3-component float vector; constructors, fields, indexer, `Equals`/`GetHashCode`/`ToString`, operators. Sibling types follow the same shape: `float2`, `float4`, and their `int`/`bool`/`double` variants (`int3`, `bool4`, `double2`, etc.).
- [float4](https://docs.unity3d.com/Packages/com.unity.mathematics@1.3/api/Unity.Mathematics.float4.html) — the 4-component float vector, commonly used for homogeneous coordinates or RGBA color.
- [quaternion](https://docs.unity3d.com/Packages/com.unity.mathematics@1.3/api/Unity.Mathematics.quaternion.html) — the rotation type, with equality/formatting support; construct via `quaternion.identity`, `quaternion.AxisAngle`, `quaternion.Euler`, `quaternion.LookRotation` rather than field-by-field.
- [float4x4](https://docs.unity3d.com/Packages/com.unity.mathematics@1.3/api/Unity.Mathematics.float4x4.html) — a 4x4 float matrix with constructors, transform methods, and operators for rotation/translation/scaling composition (`float4x4.TRS`, `float4x4.LookAt`). `float3x3` follows the same pattern for the rotation/scale-only case.

Swizzling (`v.xyz`, `v.xy`, `v.zyx`, etc.) is documented per component-combination as generated Scripting API properties on each vector type (e.g. `float3.yzxy` returning a `float4`) rather than as a single manual page — see the vector type's own API page for the full property list.
