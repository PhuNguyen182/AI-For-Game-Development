# The `math` Class & Swizzling

Covers SKILL.md steps 3–4 (elementary functions and component rearrangement).

## API
- [math](https://docs.unity3d.com/Packages/com.unity.mathematics@1.3/api/Unity.Mathematics.math.html) — the static class holding the library's math functions and constants (`math.sin`, `math.cos`, `math.sqrt`, `math.normalize`, `math.dot`, `math.cross`, `math.lerp`, `math.clamp`, `math.saturate`, `math.distance`/`math.distancesq`, and many more). Use this instead of `Mathf`/`System.Math` in `Game.Core.*` or Burst-compiled code — see [shared-core-and-burst-compatibility.md](shared-core-and-burst-compatibility.md) for why.

## Swizzling
Every vector type (`float2`/`float3`/`float4` and their `int`/`bool`/`double` variants) exposes swizzle properties as generated read/write accessors — e.g. `v.xy`, `v.xyz`, `v.zyx`, `v.xxyy` — each returning a vector sized to the number of components named. These are documented per-combination as individual Scripting API properties (for example `Unity.Mathematics.float3.yzxy`) rather than on one consolidated manual page; the type's own API page (see [vector-and-matrix-types.md](vector-and-matrix-types.md)) lists its full property set. Use swizzling to rearrange components for readability (`position.xz` for a ground-plane projection) instead of constructing a new vector field-by-field.
