# Global Illumination

Docs: Manual `Lighting` pages (Light Modes, Lighting Mode, lightmapping, lightmap UVs, Light Probes, Lighting Data Assets); API `Lightmapping`, `LightmapSettings`, `LightProbes`, `MixedLightingMode`.

**Light Mode** is per light (Realtime, Baked, Mixed). **Lighting Mode** is per scene and applies to every Mixed light at once; two Mixed lights cannot differ and nothing warns.

## Light Mode
| Mode | Produces |
|---|---|
| Realtime | Direct light and realtime shadows each frame; no indirect bounce unless realtime GI is on. Only mode that reacts to runtime change |
| Baked | Direct and indirect in lightmaps; nearly free, fully static; reaches dynamic objects only through probes |
| Mixed | Baked indirect + realtime direct; shadow behaviour from the Lighting Mode. Usual for a sun over static architecture with moving characters |

Mode is consumed at bake time: changing it invalidates the bake.

## Lighting Mode
| Mode | Shadows and cost |
|---|---|
| Baked Indirect (`MixedLightingMode.IndirectOnly`) | Mixed lights cast realtime shadows only; none beyond shadow distance. No extra memory |
| Shadowmask | Realtime inside shadow distance, baked beyond it. Extra shadowmask texture per lightmap |
| Subtractive | Cheapest. Only one directional light casts a realtime shadow, composited into baked light; dynamic objects lit flatly. Low-end mobile |

`QualitySettings.shadowmaskMode`: Shadowmask (baked shadows beyond the distance, static casters always baked) vs Distance Shadowmask (realtime for everything inside the distance including static casters: better, costlier).

## What gets baked
| Requirement | Absence produces |
|---|---|
| Contribute GI on the renderer | Mesh skipped by the lightmapper: the commonest "bake did nothing" |
| Receive GI = Lightmaps or Light Probes | Probes suit small/moving props, wrong for a wall |
| Lighting Settings Asset | Scene bakes with defaults nobody chose |
| Lighting Data Asset | Bake output per scene; version control must carry it for a build to match the Editor |
| Resolution (texels per unit) | Scales with world size: raising it on a large level multiplies bake time |

## Lightmap UVs
| Situation | Result |
|---|---|
| No second UV set and Generate Lightmap UVs off | Garbage or flat lighting |
| Overlapping charts | Light bleeds between unrelated surfaces |
| Charts packed too close for resolution | Seams; fix padding or resolution, not sample count |
| Directional Mode | Dominant light direction so normal maps respond; doubles lightmap memory |

## Light Probes (legacy)
- `LightProbeGroup`: dynamic objects interpolate between nearest probes; a region without probes borrows from the nearest, often through a wall.
- A planar probe arrangement degenerates the tetrahedralization (a flat ring lights badly).
- `LightProbes.Tetrahedralize()` rebuilds after runtime position changes.
- APV replaces this on an SRP ([probe-volumes.md](probe-volumes.md)); do not maintain both.

## Script control
- `Lightmapping.BakeAsync()`/`Bake()` (Editor), `isRunning`, `buildProgress`, `Cancel()`; `BakeMultipleScenes()` bakes scenes as one solution.
- `LightmapSettings.lightmaps`: swappable baked data for time of day without re-baking.
- `RenderSettings`: ambient, skybox, fog: scene-wide bake inputs.
