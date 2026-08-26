# Noise Functions — cnoise, snoise, cellular

Source: [noise](https://docs.unity3d.com/Packages/com.unity.mathematics@1.3/api/Unity.Mathematics.noise.html).
Covers: SKILL.md §4 — **"Choose the `noise` function by dimensionality and statistical character"**.

The three noise families and what visually distinguishes them, so the choice
is made for the effect rather than by whichever was used last. Seeding and
determinism concerns for procedural generation are
[random-numbers.md](random-numbers.md).

| Function | Effect | Use when | Source |
|---|---|---|---|
| `noise.cnoise` | Classic Perlin noise — smooth, continuous, gradient-based variation | Terrain height, smooth turbulence, anything reading as gradual drift | [noise](https://docs.unity3d.com/Packages/com.unity.mathematics@1.3/api/Unity.Mathematics.noise.html) |
| `noise.snoise` | Simplex noise — same smooth continuous character, different construction and artefact profile | The same smooth need as Perlin, where simplex's artefact profile suits better | [noise](https://docs.unity3d.com/Packages/com.unity.mathematics@1.3/api/Unity.Mathematics.noise.html) |
| `noise.cellular` | Cellular/Worley noise — discrete cell regions with distance-based boundaries | Cell-like or organic structure: biome regions, cracks, scales, stone | [noise](https://docs.unity3d.com/Packages/com.unity.mathematics@1.3/api/Unity.Mathematics.noise.html) |

| Selection axis | What it decides | Source |
|---|---|---|
| Input dimensionality | Each family is available across multiple input dimensionalities — match the sample space, so a planar generator samples with `float2` rather than wasting a `float3` lane | [noise](https://docs.unity3d.com/Packages/com.unity.mathematics@1.3/api/Unity.Mathematics.noise.html) |
| Statistical character | Smooth continuous (`cnoise`/`snoise`) versus cell-partitioned (`cellular`) | [noise](https://docs.unity3d.com/Packages/com.unity.mathematics@1.3/api/Unity.Mathematics.noise.html) |

**Critical caveat**: `cellular` is not a thresholded `snoise`. No threshold
applied to smooth continuous noise produces true cell boundaries — swapping
one family for another changes what the effect can express, not just its look.
