# Adaptive Probe Volumes

Docs: Manual `urp/probevolumes` (introduction, size and density, Baking Sets, optimize loading, changing lighting at runtime, troubleshooting, Probe Adjustment Volume, Options Override reference, Rendering Debugger); API `ProbeVolume`, `ProbeAdjustmentVolume`.

APV places and subdivides probes automatically, replacing hand-placed `LightProbeGroup`; do not combine. Requires APV enabled on the pipeline Asset (URP: set here; HDRP: `unity-hdrp-rendering` owns it and hands authoring here). Without it volumes bake and render nothing, with no report.

## Placement and density
- `ProbeVolume`: size to the traversable space; probes in unreachable geometry are baked, stored and streamed for nothing.
- Min/Max Probe Spacing: the system densifies near geometry; min governs cost where it matters, max in open space.
- Override Probe Spacing: finer probes for one interior without densifying everywhere.
- Show probes in the Scene view to confirm subdivision before spending a bake.

## Baking Sets and streaming
- Baking Set: scenes bake as one solution; required for continuous probe data across additively loaded scenes.
- Streaming: loads probe data by camera proximity; enable deliberately; makes large levels affordable on memory-bound devices.
- Probe Volumes Options Override (normal bias, view bias, leak reduction) rides the Volume framework owned by `unity-post-processing`; what it configures is this system.

## Light leaks
A probe inside a wall carries exterior light into the interior. Fix the cause: bias displaces every sample and softens contact lighting level-wide.

| Fix (in order) | Note |
|---|---|
| `ProbeAdjustmentVolume` | Invalidate, virtual-offset or re-densify probes in a region; targeted, first choice |
| Rendering layer masks | Separate which lights a region samples, so an interior never gets the exterior sun ([rendering-layers.md](rendering-layers.md)) |
| Virtual Offset | Pushes probes out of geometry at bake; resolves many leaks with no per-region work |
| Normal Bias / View Bias | Global, blunt; last |
| Rendering Debugger | Shows which probes a pixel samples |

## Runtime
- Baked APV states can be blended for time of day without a re-bake, within the documented constraints.
- Custom shaders read APV with `EvaluateAdaptiveProbeVolume()` ([custom-lighting-api.md](custom-lighting-api.md)).
