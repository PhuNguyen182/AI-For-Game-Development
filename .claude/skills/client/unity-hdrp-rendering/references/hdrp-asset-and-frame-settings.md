# HDRP Asset & Frame Settings

Covers SKILL.md step 2 (global vs. per-camera feature configuration).

## Manual
- [The High Definition Render Pipeline Asset](https://docs.unity3d.com/Packages/com.unity.render-pipelines.high-definition@17.5/manual/HDRP-Asset.html) — global feature toggles; Frame Settings can only turn off what this enables.

## Scripting API
- [`UnityEngine.Rendering.HighDefinition` namespace index](https://docs.unity3d.com/Packages/com.unity.render-pipelines.high-definition@17.5/api/UnityEngine.Rendering.HighDefinition.html) — browse from here for `FrameSettings`, `HDRenderPipelineAsset`.
- [`HDAdditionalCameraData`](https://docs.unity3d.com/Packages/com.unity.render-pipelines.high-definition@17.5/api/UnityEngine.Rendering.HighDefinition.HDAdditionalCameraData.html) — per-camera HDRP-specific parameters, including Frame Settings overrides and the Volume-interpolation layer mask.
