# Global Illumination — Light Modes, Baking, Lightmap UVs, Light Probes

Sources: [Direct and indirect lighting](https://docs.unity3d.com/Manual/direct-and-indirect-lighting.html), [Light Modes](https://docs.unity3d.com/Manual/LightModes-introduction.html), [Lighting Mode](https://docs.unity3d.com/Manual/lighting-mode.html), [Lightmapping](https://docs.unity3d.com/Manual/Lightmapping.html), [Lightmap UVs](https://docs.unity3d.com/Manual/LightingGiUvs.html), [Light Probes](https://docs.unity3d.com/Manual/LightProbes.html).
Covers: SKILL.md §4 — **"Set each light's Mode before anything is authored around it"**, **"Flag the geometry and give it lightmap UVs before blaming the lightmapper"**.

Two settings decide almost everything about a bake, and they sit at different
scopes that are easy to confuse. **Light Mode** is per light — Realtime,
Baked, or Mixed. **Lighting Mode** is per scene and applies to every Mixed
light at once. There is no way to give two Mixed lights different Lighting
Modes, and nothing in the Inspector says so.

## Contents

- [Light Mode — per light](#light-mode--per-light)
- [Lighting Mode — per scene](#lighting-mode--per-scene)
- [What actually gets baked](#what-actually-gets-baked)
- [Lightmap UVs](#lightmap-uvs)
- [Light Probes](#light-probes)
- [Bake control from script](#bake-control-from-script)

## Light Mode — per light

| Mode | What it produces, and what it costs | Source |
|---|---|---|
| Realtime | Direct light and realtime shadows every frame, no bake, no indirect bounce unless realtime GI is enabled. The only mode that reacts to a light moving or changing at runtime | [Choose a Light Mode](https://docs.unity3d.com/Manual/LightModes-choose.html) |
| Baked | Direct and indirect both written into lightmaps. Nearly free at runtime and completely static — the light contributes nothing to dynamic objects except through probes | [Choose a Light Mode](https://docs.unity3d.com/Manual/LightModes-choose.html) |
| Mixed | Baked indirect plus realtime direct, with shadow behaviour decided by the scene's Lighting Mode below. The usual choice for a sun over static architecture with moving characters | [Light Modes](https://docs.unity3d.com/Manual/LightModes-introduction.html) |

Mode is consumed at bake time. Changing it afterwards invalidates the bake
rather than taking effect, and a runtime write to `lightmapBakeType` does not
re-light anything.

## Lighting Mode — per scene

| Lighting Mode | Shadow behaviour and cost | Source |
|---|---|---|
| Baked Indirect | Mixed lights cast **realtime shadows only**, so shadows stop at the shadow distance and nothing is baked to fill in beyond it. Highest quality near the camera, no extra memory | [Lighting Mode](https://docs.unity3d.com/Manual/lighting-mode.html) |
| Shadowmask | Realtime shadows inside the shadow distance, baked shadowmask beyond it — the combination that lets a large level keep distant shadows. Costs an extra shadowmask texture per lightmap, and a Quality Settings choice between Shadowmask and Distance Shadowmask | [Lighting Mode](https://docs.unity3d.com/Manual/lighting-mode.html) |
| Subtractive | Cheapest. Only **one** directional light casts a realtime shadow and it is composited into the baked lighting; everything else is fully baked, and dynamic objects are lit flatly. A low-end mobile choice, not a quality one | [Lighting Mode](https://docs.unity3d.com/Manual/lighting-mode.html) |
| `MixedLightingMode` | The scripting enum — `IndirectOnly`, `Shadowmask`, `Subtractive` | [MixedLightingMode](https://docs.unity3d.com/ScriptReference/MixedLightingMode.html) |

`QualitySettings.shadowmaskMode` then picks between **Shadowmask** (baked
shadows for anything outside the shadow distance, static casters always baked)
and **Distance Shadowmask** (realtime shadows for everything inside the
distance, including static casters — better looking, more expensive).

## What actually gets baked

| Requirement | What its absence produces | Source |
|---|---|---|
| Contribute GI on the renderer | The mesh is skipped by the lightmapper entirely and stays lit only by realtime lights — the single most common "the bake did nothing" cause | [Set up your scene for baking](https://docs.unity3d.com/Manual/Lightmapping.html) |
| Receive Global Illumination — Lightmaps or Light Probes | A Contribute-GI object set to Light Probes takes probe lighting instead of a lightmap, which is correct for small or moving props and wrong for a wall | [Set up your scene for baking](https://docs.unity3d.com/Manual/Lightmapping.html) |
| A Lighting Settings Asset | Bake settings are per scene and stored in an asset; a scene without one uses defaults that were never chosen | [Lighting window](https://docs.unity3d.com/Manual/lighting-window.html) |
| The Lighting Data Asset | The bake output, per scene. It is what version control must carry for a build to look like the editor | [Lighting Data Assets](https://docs.unity3d.com/Manual/LightingDataAsset.html) |
| Lightmap resolution and padding | Resolution is texels per unit, so it scales with world size — raising it on a large level multiplies bake time rather than adding a fixed cost | [Lightmapping settings](https://docs.unity3d.com/Manual/Lightmaps-reference.html) |

## Lightmap UVs

| Situation | Result | Source |
|---|---|---|
| Model has no second UV set and Generate Lightmap UVs is off | Nothing valid to bake into; the mesh comes back with garbage or flat lighting | [Generate lightmap UVs](https://docs.unity3d.com/Manual/LightingGiUvs-GeneratingLightmappingUVs.html) |
| Overlapping UV charts | Light bleeds between unrelated surfaces — the classic patch of ceiling light on a floor | [Introduction to lightmap UVs](https://docs.unity3d.com/Manual/LightingGiUvs.html) |
| Charts packed too close for the lightmap resolution | Seams at chart borders; the fix is padding or resolution, not more samples | [Troubleshooting baked lightmaps](https://docs.unity3d.com/Manual/Lightmapping-troubleshooting.html) |
| Directional Mode | Stores a dominant light direction alongside colour so normal maps still respond under baked light — doubles lightmap memory | [Directional Mode](https://docs.unity3d.com/Manual/LightmappingDirectional.html) |

## Light Probes

| Piece | What it decides | Source |
|---|---|---|
| `LightProbeGroup` | Where legacy probes are baked. Dynamic objects interpolate between the nearest probes, so a region with no probes lights dynamic objects from whatever is nearest — often through a wall | [Place Light Probes](https://docs.unity3d.com/Manual/class-LightProbeGroup.html) |
| Tetrahedralization | Probes form a tetrahedral volume; a **planar** arrangement degenerates it, which is why a single flat ring of probes lights badly | [Light Probe data format](https://docs.unity3d.com/Manual/LightProbes-TechnicalInformation.html) |
| `LightProbes.Tetrahedralize()` | Rebuilds that structure after probe positions change at runtime | [LightProbes API](https://docs.unity3d.com/ScriptReference/LightProbes.html) |
| Relationship to APV | Adaptive Probe Volumes replace this workflow on an SRP and place probes automatically — see [probe-volumes.md](probe-volumes.md). Do not maintain both | [Adaptive Probe Volumes](https://docs.unity3d.com/Manual/urp/probevolumes-concept.html) |

## Bake control from script

| Member | What it is for | Source |
|---|---|---|
| `Lightmapping.BakeAsync()` / `Bake()` | Editor-time bake trigger; `isRunning` and `buildProgress` report state, `Cancel()` stops it | [Lightmapping API](https://docs.unity3d.com/ScriptReference/Lightmapping.html) |
| `Lightmapping.BakeMultipleScenes()` | Bakes several scenes as one lighting solution — the multi-scene equivalent of a Baking Set | [Lightmapping API](https://docs.unity3d.com/ScriptReference/Lightmapping.html) |
| `LightmapSettings.lightmaps` | The baked data at runtime, swappable for a time-of-day set — the supported way to change baked lighting without re-baking | [LightmapSettings](https://docs.unity3d.com/ScriptReference/LightmapSettings.html) |
| `RenderSettings` | Ambient source and intensity, skybox, fog — scene-wide inputs the bake reads, not per-light settings | [RenderSettings](https://docs.unity3d.com/ScriptReference/RenderSettings.html) |
