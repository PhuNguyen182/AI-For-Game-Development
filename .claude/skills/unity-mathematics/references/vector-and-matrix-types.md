# Vector & Matrix Types

Sources: [a] manual/index.html, [b] manual/getting-started.html, [c] api/Unity.Mathematics.float3.html (also float4, quaternion, float4x4 pages) — below the SKILL.md `Docs:` base.

- Shader-like syntax by design; `using Unity.Mathematics;` exposes the whole library [b].
- Built into the Editor from Unity 6.5; no install step there [a].
- Burst treats these as first-class types and optimizes them directly [b].

## Choosing a type

| Type | Use when |
|---|---|
| `float3` | Genuinely 3D data: position, direction, scale |
| `float2` / `float4` | Planar data / a real 4-component value (homogeneous coordinate, RGBA) |
| `int3`, `bool4`, `double2` etc. | Integer indices, per-lane masks, double precision; same shape as `floatN` |
| `quaternion` | Any rotation outside a MonoBehaviour's own `Transform` access |
| `float4x4` | Full transform composition including translation |
| `float3x3` | Rotation and scale only; smaller and cheaper |

## Factories

| Factory | Effect |
|---|---|
| `quaternion.identity` | No rotation |
| `quaternion.AxisAngle` | Rotation about an axis by an angle |
| `quaternion.Euler` | From Euler angles |
| `quaternion.LookRotation` | Aligns forward to a direction |
| `float4x4.TRS` | Translation, rotation, scale in one call |
| `float4x4.LookAt` | Look-at transform |

**Caveat:** a `quaternion` built field-by-field is not normalized and not reported as invalid: a silent correctness risk.
