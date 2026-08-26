# HDRP Asset & Frame Settings — Ceiling and Mask

Sources: [The High Definition Render Pipeline Asset](https://docs.unity3d.com/Packages/com.unity.render-pipelines.high-definition@17.5/manual/HDRP-Asset.html), [HDAdditionalCameraData](https://docs.unity3d.com/Packages/com.unity.render-pipelines.high-definition@17.5/api/UnityEngine.Rendering.HighDefinition.HDAdditionalCameraData.html).
Covers: SKILL.md §4 — **"Know whether you are editing the Asset's ceiling or a Frame Settings mask"**.

The two-layer model that decides whether a feature exists at all and whether a
given camera uses it. Nearly every "I enabled it and nothing happened" report
in HDRP resolves here.

| Subject | What it decides | Source |
|---|---|---|
| HD Render Pipeline Asset | The **ceiling**: which features are compiled into the build at all, per quality level if several Assets exist | [HDRP Asset](https://docs.unity3d.com/Packages/com.unity.render-pipelines.high-definition@17.5/manual/HDRP-Asset.html) |
| Frame Settings | A **mask** under that ceiling — it can disable what the Asset enabled, never enable what the Asset disabled | [HDRP Asset](https://docs.unity3d.com/Packages/com.unity.render-pipelines.high-definition@17.5/manual/HDRP-Asset.html) |
| Default Frame Settings | Live on the Asset and apply to cameras, reflection probes, and baked probes as separate sets — a probe can differ from a camera by default | [HDRP Asset](https://docs.unity3d.com/Packages/com.unity.render-pipelines.high-definition@17.5/manual/HDRP-Asset.html) |
| Per-camera override | `HDAdditionalCameraData` carries the camera's own Frame Settings overrides plus its Volume-interpolation layer mask | [HDAdditionalCameraData](https://docs.unity3d.com/Packages/com.unity.render-pipelines.high-definition@17.5/api/UnityEngine.Rendering.HighDefinition.HDAdditionalCameraData.html) |
| `FrameSettings` / `HDRenderPipelineAsset` types | The scripted entry points for both layers | [HighDefinition namespace](https://docs.unity3d.com/Packages/com.unity.render-pipelines.high-definition@17.5/api/UnityEngine.Rendering.HighDefinition.html) |

**Critical caveat**: an ineffective Frame Settings toggle produces no warning,
no log, and no visual change. Because the UI shows the toggle as on, the
setting appears correct while the Asset above it has already excluded the
feature — always diagnose downward from the Asset.
