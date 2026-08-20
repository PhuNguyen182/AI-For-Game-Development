# Root Links — Post-Processing Landing Pages

The starting landing pages for Unity's post-processing documentation, spanning the render-pipeline-agnostic overview, the effect-availability comparison across Built-in RP/URP/HDRP/legacy PPv2, and URP's own post-processing/Volumes/custom-effect landing pages. Each fans out into the topic-specific reference files listed in [SKILL.md](../SKILL.md).

## Manual — General (render-pipeline-agnostic)
- [Post-processing](https://docs.unity3d.com/6000.5/Documentation/Manual/post-processing-and-full-screen-effects.html) — top-level post-processing landing page; links out to the Built-in/URP/HDRP/legacy-PPv2 entry points below.
- [Introduction to post-processing](https://docs.unity3d.com/6000.5/Documentation/Manual/PostProcessingOverview.html) — explains that each render pipeline (Built-in, URP, HDRP) has its own post-processing solution and links to each.
- [Post-processing effect availability reference](https://docs.unity3d.com/6000.5/Documentation/Manual/post-processing-effect-availability-reference.html) — per-effect comparison table across Built-in RP (via Post Processing Stack v2), URP, and HDRP; see [effect-availability-and-effect-list.md](effect-availability-and-effect-list.md) for the full fan-out.
- [Render pipeline feature comparison](https://docs.unity3d.com/6000.5/Documentation/Manual/render-pipelines-feature-comparison.html) — broader Built-in/URP/HDRP feature comparison, useful context for confirming which pipeline a post-processing effect is actually available on.

## Manual — URP
- [Post-processing and full-screen effects in URP](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/post-processing-and-full-screen-effects-urp.html) — URP's post-processing landing page; links to Volumes, the Effect List, and custom post-processing.
- [Volumes in URP](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/volumes-landing-page.html) — the Volume system landing page; see [volumes.md](volumes.md) for the full fan-out.
- [Post-processing Volume Overrides reference for URP](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/EffectList.html) — index of every built-in post-processing Volume Override (Bloom, Tonemapping, etc.); see [effect-availability-and-effect-list.md](effect-availability-and-effect-list.md).
- [Custom post-processing in URP](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/post-processing/custom-post-processing.html) — landing page for authoring a custom full-screen post-processing effect; see [custom-post-processing.md](custom-post-processing.md).
- [On-tile post-processing](https://docs.unity3d.com/6000.5/Documentation/Manual/on-tile-post-processing.html) — tile-based GPU (mobile) post-processing performance considerations.

## Package — Legacy Post Processing Stack v2 (Built-in Render Pipeline)
- [Post Processing (com.unity.postprocessing) package index](https://docs.unity3d.com/Packages/com.unity.postprocessing@3.5/api/index.html) — legacy package API root, used with the Built-in Render Pipeline before URP's Volume-based post-processing; see [postprocessing-v2-legacy.md](postprocessing-v2-legacy.md).

## Notes
- "Volume" here (the URP post-processing/Volume system: `Volume`, `VolumeProfile`, `VolumeComponent`) is unrelated to `unity-lighting`'s Adaptive Probe Volumes (`ProbeVolume`) — same word, different systems, both documented in their respective skills.
- The Built-in Render Pipeline has no native Volume-based post-processing of its own — it relies entirely on the legacy Post Processing Stack v2 package (`com.unity.postprocessing`), not URP's Volume system.
