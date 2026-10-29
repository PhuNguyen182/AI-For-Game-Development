# The math Class, Swizzling and noise

Sources: [a] api/Unity.Mathematics.math.html, [b] api/Unity.Mathematics.float3.html, [c] api/Unity.Mathematics.noise.html — below the SKILL.md `Docs:` base.

## math members [a]

| Member | Fact that decides |
|---|---|
| `math.normalize` | Unit vector; use when a direction, not a displacement, is needed |
| `math.dot` / `math.cross` | Angle tests and projection / perpendicular axis |
| `math.distance` | True distance (square root); use when the value itself is used |
| `math.distancesq` | No square root; use for threshold comparison, pre-squaring the threshold |
| `math.saturate` | Replaces `Mathf.Clamp01` |
| `math.clamp` / `math.lerp` | Replace `Mathf.Clamp` / `Mathf.Lerp` |
| `math.sin` / `cos` / `sqrt` | Replace `Mathf`/`System.Math` equivalents |

**Caveat:** `math` and `Mathf`/`System.Math` are not guaranteed to agree bit-for-bit; verify precision-sensitive comparisons.

## Swizzling [b]

- Result width follows the name: `v.xy` is `float2`, `v.xyz` `float3`, `v.xxyy` `float4`.
- Repetition and reordering are legal (`v.zyx`, `v.xxyy`) on every vector type, including `int`/`bool`/`double` variants.
- Read/write generated properties: no allocation.
- Each combination is its own API property (e.g. `float3.yzxy`); see the type's API page for the list.

## noise [c]

| Function | Character | Use when |
|---|---|---|
| `noise.cnoise` | Classic Perlin: smooth, gradient-based | Terrain height, gradual drift |
| `noise.snoise` | Simplex: smooth, different artefact profile | Same need as Perlin where simplex suits |
| `noise.cellular` | Worley: discrete cells, distance boundaries | Biome regions, cracks, scales, stone |

Each family exists at several input dimensionalities: sample a planar generator with `float2`, not `float3`.

**Caveat:** `cellular` is not a thresholded `snoise`; no threshold on smooth noise yields true cell boundaries.
