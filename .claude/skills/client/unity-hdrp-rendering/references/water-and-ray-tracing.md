# Water System, Ray Tracing & Path Tracing

Sources: [Capabilities of the Water System](https://docs.unity3d.com/Packages/com.unity.render-pipelines.high-definition@17.5/manual/WaterSystem-Overview.html), [Ray tracing hardware requirements](https://docs.unity3d.com/Packages/com.unity.render-pipelines.high-definition@17.5/manual/raytracing-requirements.html), [Path tracing limitations](https://docs.unity3d.com/Packages/com.unity.render-pipelines.high-definition@17.5/manual/path-tracing-limitations.html).
Covers: SKILL.md §4 — **"Gate every PC and console class feature on the Tech Spec's platform scope"**, **"Check documented incompatibilities before combining high-fidelity features"**.

## Contents
- [Water System](#water-system)
- [Ray and path tracing](#ray-and-path-tracing)

The features that are not merely expensive but conditional — on platform, on
hardware, and on what else is enabled in the frame.

## Water System

| Subject | What it decides | Source |
|---|---|---|
| Surface types | Pool, River, and Ocean-Sea-Lake, each with a different simulation scope and cost | [Water System overview](https://docs.unity3d.com/Packages/com.unity.render-pipelines.high-definition@17.5/manual/WaterSystem-Overview.html) |
| Enabling it | Requires the feature enabled in the pipeline configuration before any water surface renders | [Use the water system](https://docs.unity3d.com/Packages/com.unity.render-pipelines.high-definition@17.5/manual/water-use-the-water-system-in-your-project.html) |
| Settings and properties | The per-surface simulation and appearance parameters | [Water settings and properties](https://docs.unity3d.com/Packages/com.unity.render-pipelines.high-definition@17.5/manual/settings-and-properties-related-to-the-water-system.html) |
| Scripting | Runtime queries and control over the simulation, for gameplay that reacts to the surface | [Water System scripting](https://docs.unity3d.com/Packages/com.unity.render-pipelines.high-definition@17.5/manual/WaterSystem-scripting.html) |

## Ray and path tracing

| Subject | What it decides | Source |
|---|---|---|
| Hardware requirement | Ray tracing needs capable GPU hardware and a supported API — a PC or console target is necessary but not sufficient | [Ray tracing requirements](https://docs.unity3d.com/Packages/com.unity.render-pipelines.high-definition@17.5/manual/raytracing-requirements.html) |
| Setup | Driven through the HDRP Wizard under `Window > Rendering`, which validates the project's configuration | [Set up ray tracing](https://docs.unity3d.com/Packages/com.unity.render-pipelines.high-definition@17.5/manual/Ray-Tracing-Getting-Started.html) |
| Global parameters | Ray-tracing settings applying across effects, authored as overrides | [Ray tracing settings](https://docs.unity3d.com/Packages/com.unity.render-pipelines.high-definition@17.5/manual/Ray-Tracing-Settings.html) |
| Ray-traced reflections | The most commonly requested ray-traced effect, with its own quality and cost controls | [Ray-traced reflections](https://docs.unity3d.com/Packages/com.unity.render-pipelines.high-definition@17.5/manual/Ray-Traced-Reflections.html) |
| Path tracing | A different renderer entirely, converging over frames — not a quality setting on the rasterizer | [Path tracing](https://docs.unity3d.com/Packages/com.unity.render-pipelines.high-definition@17.5/manual/Ray-Tracing-Path-Tracing.html) |
| Path tracing limitations | A documented list of what it does not support, including Local Volumetric Fog | [Path tracing limitations](https://docs.unity3d.com/Packages/com.unity.render-pipelines.high-definition@17.5/manual/path-tracing-limitations.html) |
| Ray tracing versus volumetrics | General ray tracing is likewise not compatible with volumetric fog | [Path tracing limitations](https://docs.unity3d.com/Packages/com.unity.render-pipelines.high-definition@17.5/manual/path-tracing-limitations.html) |

**Critical caveat**: an unsupported combination does not error. The effect that
loses simply does not appear in the frame, so a scene combining path tracing
with volumetric fog looks like a fog authoring problem rather than an
incompatibility — check the limitation list before debugging the effect.
