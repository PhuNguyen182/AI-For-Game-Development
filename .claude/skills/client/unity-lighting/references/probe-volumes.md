# Adaptive Probe Volumes — Placement, Density, Baking Sets, Leaks

Sources: [Adaptive Probe Volumes in URP](https://docs.unity3d.com/Manual/urp/probevolumes.html), [Introduction to Adaptive Probe Volumes](https://docs.unity3d.com/Manual/urp/probevolumes-concept.html), [Configure size and density](https://docs.unity3d.com/Manual/urp/probevolumes-changedensity.html), [Troubleshooting Adaptive Probe Volumes](https://docs.unity3d.com/Manual/urp/probevolumes-fixissues.html).
Covers: SKILL.md §4 — **"Author Adaptive Probe Volumes for dynamic objects instead of a legacy Light Probe Group"**, **"Treat an APV light leak as a placement problem before reaching for bias"**.

APV places probes automatically inside a volume and subdivides them toward
geometry, replacing the hand-placed `LightProbeGroup` workflow. The two are
not combined — a project on APV stops maintaining probe groups. Everything
here assumes the pipeline Asset already has APV enabled — a URP project sets
that toggle as part of this setup, while on HDRP `unity-hdrp-rendering` owns
it and hands authoring here. Without it the volumes bake and render nothing,
and nothing reports why.

## Contents

- [Placement and density](#placement-and-density)
- [Baking Sets and streaming](#baking-sets-and-streaming)
- [Light leaks](#light-leaks)
- [Runtime](#runtime)

## Placement and density

| Setting | What it decides | Source |
|---|---|---|
| `ProbeVolume` component | Marks the region the system considers. Sized to the **traversable** space, not the whole level — probes in geometry nothing can reach are baked, stored, and streamed for nothing | [ProbeVolume API](https://docs.unity3d.com/Packages/com.unity.render-pipelines.core@17.6/api/UnityEngine.Rendering.ProbeVolume.html) |
| Min / Max Probe Spacing | The subdivision bounds. The system densifies near geometry automatically, so the min governs cost in the places that matter and the max governs it in open space | [Configure size and density](https://docs.unity3d.com/Manual/urp/probevolumes-changedensity.html) |
| Override Probe Spacing | Per-volume override, for a single interior needing finer probes than the level default without densifying everywhere | [Configure size and density](https://docs.unity3d.com/Manual/urp/probevolumes-changedensity.html) |
| Display in Scene view | Probe visualisation is the only practical way to see subdivision actually landed where intended before spending a bake | [Display Adaptive Probe Volumes](https://docs.unity3d.com/Manual/urp/probevolumes-showandadjust.html) |

## Baking Sets and streaming

| Piece | What it decides | Source |
|---|---|---|
| Baking Set | Groups scenes that bake as one lighting solution — required for an additively loaded level to have continuous probe data across its scene boundaries | [Bake multiple scenes with Baking Sets](https://docs.unity3d.com/Manual/urp/probevolumes-usebakingsets.html) |
| Streaming | Loads probe data by camera proximity instead of holding the whole set resident. Must be enabled deliberately, and it is what makes a large level's APV data affordable on a memory-bound device | [Optimize loading APV data](https://docs.unity3d.com/Manual/urp/probevolumes-streaming.html) |
| Probe Volumes Options Override | A Volume override carrying the per-region sampling settings — normal bias, view bias, leak reduction. Note it rides the post-processing Volume framework owned by `unity-post-processing`, while what it configures is this system | [Options Override reference](https://docs.unity3d.com/Manual/urp/probevolumes-options-override-reference.html) |

## Light leaks

The characteristic APV failure: a probe falls inside a wall, so it carries
exterior lighting, and interior surfaces interpolating against it pick up the
sky. Fix the cause before the symptom — bias settings hide a leak by
displacing every sample, which softens contact lighting across the level.

| Fix | What it does, and its cost | Source |
|---|---|---|
| `ProbeAdjustmentVolume` | Overrides probes in a marked region — invalidate them, force them virtual-offset, or change their density. The targeted fix, and the first to reach for | [Probe Adjustment Volume reference](https://docs.unity3d.com/Manual/urp/probevolumes-adjustment-volume-component-reference.html) |
| Rendering layer masks | Separates which lights an APV region samples, so an interior cell never receives the exterior sun — see [rendering-layers.md](rendering-layers.md) | [Prevent light leaks with rendering layer masks](https://docs.unity3d.com/Manual/urp/features/rendering-layer-masks-apv-landing.html) |
| Virtual Offset | Pushes probes out of geometry at bake time, resolving many leaks without any per-region authoring | [Troubleshooting APV](https://docs.unity3d.com/Manual/urp/probevolumes-fixissues.html) |
| Normal Bias / View Bias | Global sampling offsets. Effective and blunt — they trade the leak for softened or displaced lighting everywhere, which is why they come last | [Options Override reference](https://docs.unity3d.com/Manual/urp/probevolumes-options-override-reference.html) |
| Rendering Debugger | Shows which probes a pixel samples, which turns leak diagnosis from guessing into reading | [Rendering Debugger](https://docs.unity3d.com/Manual/urp/features/rendering-debugger.html) |

## Runtime

| Capability | What it allows | Source |
|---|---|---|
| Changing lighting at runtime | Baked APV states can be blended for a time-of-day change without a re-bake, within the documented workflow's constraints | [Changing lighting at runtime](https://docs.unity3d.com/Manual/urp/probe-volumes-change-lighting-at-runtime.html) |
| Shader-side sampling | `EvaluateAdaptiveProbeVolume()` is what a custom lit shader calls to read APV — see [custom-lighting-api.md](custom-lighting-api.md) | [Use indirect lighting in a custom URP shader](https://docs.unity3d.com/Manual/urp/use-built-in-shader-methods-indirect-lighting.html) |
