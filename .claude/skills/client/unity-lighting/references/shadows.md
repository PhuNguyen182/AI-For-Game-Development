# Shadows

Covers real-time and baked shadow fundamentals in Unity (shadow mapping, cascades, distance, bias, troubleshooting) and how those concepts carry into URP-specific shadow configuration (shadow resolution tiers, screen space shadows, cascade visualization, URP troubleshooting).

## Manual — General
- [Shadows](https://docs.unity3d.com/6000.5/Documentation/Manual/Shadows.html)
- [Enable shadows](https://docs.unity3d.com/6000.5/Documentation/Manual/shadow-configuration.html)
- [Real-time shadows](https://docs.unity3d.com/6000.5/Documentation/Manual/shadow-realtime.html)
- [Shadow mapping](https://docs.unity3d.com/6000.5/Documentation/Manual/shadow-mapping.html)
- [Set shadow distance in a scene](https://docs.unity3d.com/6000.5/Documentation/Manual/shadow-distance.html)
- [Shadow cascades](https://docs.unity3d.com/6000.5/Documentation/Manual/shadow-cascades-landing.html)
- [Introduction to shadow cascades](https://docs.unity3d.com/6000.5/Documentation/Manual/shadow-cascades.html)
- [Configure shadow cascades](https://docs.unity3d.com/6000.5/Documentation/Manual/shadow-cascades-use.html)
- [Performance impact of shadow cascades](https://docs.unity3d.com/6000.5/Documentation/Manual/shadow-cascades-performance.html)
- [Implementation details of shadow cascades](https://docs.unity3d.com/6000.5/Documentation/Manual/shadow-cascades-implementation-details.html)
- [Troubleshooting shadows](https://docs.unity3d.com/6000.5/Documentation/Manual/ShadowPerformance.html)

## Manual — URP
- [Shadows in URP](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/Shadows-in-URP.html)
- [Configure shadow resolution in the Universal Render Pipeline](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/shadow-resolution-urp.html)
- [Add screen space shadows in URP](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/renderer-feature-screen-space-shadows.html)
- [Visualize shadow cascades](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/shadow-cascades-visualize.html)
- [Troubleshooting shadows in URP](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/shadows-troubleshooting-urp.html)
- [Optimize shadow rendering in URP](https://docs.unity3d.com/6000.5/Documentation/Manual/shadows-optimization.html)

## Scripting API
- [Light](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/Light.html) — shadow-related members: `shadows`, `shadowStrength`, `shadowBias`, `shadowNormalBias`, `shadowNearPlane`, `shadowCustomResolution`, `shadowResolution`, `shadowAngle` (directional light soft-edge, Editor only), `shadowMatrixOverride`/`useShadowMatrixOverride`.
- [QualitySettings](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/QualitySettings.html) — shadow-related members: `shadows`, `shadowCascades`, `shadowDistance`, `shadowResolution`, `shadowProjection`, `shadowmaskMode`, `shadowNearPlaneOffset`, `shadowCascade2Split`, `shadowCascade4Split`.
- [UniversalAdditionalLightData](https://docs.unity3d.com/Packages/com.unity.render-pipelines.universal@17.0/api/UnityEngine.Rendering.Universal.UniversalAdditionalLightData.html) — URP per-light extension component; shadow-related members: `additionalLightsShadowResolutionTier`, `softShadowQuality`, `usePipelineSettings`, `customShadowLayers`, `shadowRenderingLayers`.
- [UniversalRenderPipelineAsset](https://docs.unity3d.com/Packages/com.unity.render-pipelines.universal@17.0/api/UnityEngine.Rendering.Universal.UniversalRenderPipelineAsset.html) — shadow-related members: `shadowDistance`, `shadowCascadeCount`, `cascade2Split`/`cascade3Split`/`cascade4Split`, `cascadeBorder`, `shadowDepthBias`, `shadowNormalBias`, `mainLightShadowmapResolution`, `additionalLightsShadowmapResolution`, `additionalLightsShadowResolutionTierLow`/`...TierMedium`/`...TierHigh`, `supportsMainLightShadows`, `supportsAdditionalLightShadows`, `supportsSoftShadows`, `conservativeEnclosingSphere`, `numIterationsEnclosingSphere`.
