# Unity Lighting — Scripting API Index

Consolidated Scripting API reference for Unity lighting: engine-core `UnityEngine` lighting/GI classes plus the URP package API surface for per-light and pipeline-level lighting/shadow configuration. Each entry links the confirmed ScriptReference/package API page with a one-line note of what it covers.

## Light component

- [Light](https://docs.unity3d.com/ScriptReference/Light.html) — the core light component. Key members: `type`, `intensity`, `color`, `range`, `spotAngle`, `innerSpotAngle`, `shadows`, `shadowStrength`, `shadowBias`, `shadowNormalBias`, `cookie`, `cullingMask`, `renderMode`, `bounceIntensity`, `lightmapBakeType`, `colorTemperature`, `useColorTemperature`, `renderingLayerMask`. All members are documented inline on this one class page — no separate member sub-pages exist.

## Light-related enums

- [LightType](https://docs.unity3d.com/ScriptReference/LightType.html) — light shape/kind: `Spot`, `Directional`, `Point`, `Rectangle`, `Disc`, `Pyramid`, `Box`, `Tube`.
- [LightShadows](https://docs.unity3d.com/ScriptReference/LightShadows.html) — shadow cast mode: `None`, `Hard`, `Soft`.
- [LightRenderMode](https://docs.unity3d.com/ScriptReference/LightRenderMode.html) — per-pixel vs per-vertex rendering: `Auto`, `ForcePixel`, `ForceVertex`.
- [LightShape](https://docs.unity3d.com/ScriptReference/LightShape.html) — **obsolete**; page explicitly says to use `LightType.Spot`, `LightType.Pyramid`, or `LightType.Box` instead.
- [LightmapBakeType](https://docs.unity3d.com/ScriptReference/LightmapBakeType.html) — how much of a light's contribution is baked: `Realtime`, `Baked`, `Mixed`.
- [LightShadowCasterMode](https://docs.unity3d.com/ScriptReference/LightShadowCasterMode.html) — Shadowmask caster culling for mixed lights: `Default`, `ShadowMask`, `DistanceShadowMask`.

## Ambient, skybox & fog

- [RenderSettings](https://docs.unity3d.com/ScriptReference/RenderSettings.html) — scene-wide environment lighting. Key members: `ambientMode`, `ambientIntensity`, `ambientLight`, `ambientSkyColor`/`ambientEquatorColor`/`ambientGroundColor`, `skybox`, `ambientProbe`, `defaultReflectionMode`, `reflectionIntensity`, `reflectionBounces`, `fog`/`fogColor`/`fogMode`/`fogDensity`/`fogStartDistance`/`fogEndDistance`, `subtractiveShadowColor`, `sun`.

## Lightmaps & baking

- [LightmapSettings](https://docs.unity3d.com/ScriptReference/LightmapSettings.html) — static class storing the loaded scene's lightmap data. Key members: `lightmaps`, `lightmapsMode`, `lightProbes`.
- [LightmapData](https://docs.unity3d.com/ScriptReference/LightmapData.html) — one scene lightmap entry. Key members: `lightmapColor`, `lightmapDir` (CombinedDirectional mode), `shadowMask` (Shadowmask mixed mode).
- [Lightmapping](https://docs.unity3d.com/ScriptReference/Lightmapping.html) — static class that drives GI baking. Key members: `Bake()`, `BakeAsync()`, `BakeMultipleScenes()`, `Clear()`, `ClearDiskCache()`, `isRunning`; events `bakeStarted`, `bakeCompleted`, `bakeCancelled`, `lightingDataUpdated`.

## Light probes

- [LightProbes](https://docs.unity3d.com/ScriptReference/LightProbes.html) — baked probe data for the loaded scenes. Key members: `GetInterpolatedProbe()`, `Tetrahedralize()`/`TetrahedralizeAsync()`, `GetSharedLightProbesForScene()`, `CalculateInterpolatedLightAndOcclusionProbes()`, `positions`, `count`, `bakedProbes`, `cellCount`; events `lightProbesUpdated`, `tetrahedralizationCompleted`.
- [LightProbeGroup](https://docs.unity3d.com/ScriptReference/LightProbeGroup.html) — component marking where to bake light probes. Key members: `probePositions`, ringing-removal option (editor-only).
- [LightProbeProxyVolume](https://docs.unity3d.com/ScriptReference/LightProbeProxyVolume.html) — **deprecated**; page states it is deprecated now that the Built-In Render Pipeline is deprecated. Page shows only inherited `Behaviour`/`Component`/`Object` members, no custom API of its own documented.

## Reflection probes

- [ReflectionProbe](https://docs.unity3d.com/ScriptReference/ReflectionProbe.html) — component for baked/realtime environment reflections. Key members: `mode`, `refreshMode`, `timeSlicingMode`, `intensity`, `boxProjection`, `size`, `cullingMask`, `resolution`, `importance`.
- [Rendering.ReflectionProbeMode](https://docs.unity3d.com/ScriptReference/Rendering.ReflectionProbeMode.html) — `Baked`, `Realtime`, `Custom`.
- [Rendering.ReflectionProbeRefreshMode](https://docs.unity3d.com/ScriptReference/Rendering.ReflectionProbeRefreshMode.html) — `OnAwake`, `EveryFrame`, `ViaScripting`.
- [Rendering.ReflectionProbeTimeSlicingMode](https://docs.unity3d.com/ScriptReference/Rendering.ReflectionProbeTimeSlicingMode.html) — `NoTimeSlicing`, `AllFacesAtOnce`, `IndividualFaces`.

## Quality settings (shadows)

- [QualitySettings](https://docs.unity3d.com/ScriptReference/QualitySettings.html) — global quality tier config. Shadow-related members: `shadows`, `shadowCascades`, `shadowDistance`, `shadowResolution`, `shadowProjection`, `shadowmaskMode`, `shadowNearPlaneOffset`.

## Rendering layers

- [RenderingLayerMask](https://docs.unity3d.com/ScriptReference/RenderingLayerMask.html) — struct representing the 32-bit rendering-layer bitmask (configured under Tags and Layers) used to selectively couple lights/renderers in an SRP. Key members: `defaultRenderingLayerMask`, `value`, `GetDefinedRenderingLayerCount()`, `GetDefinedRenderingLayerNames()`, `GetMask()`, `NameToRenderingLayer()`, `RenderingLayerToName()`.
  Note: `Light.renderingLayerMask` exists (documented on the `Light` page above) and works with an SRP's own renderer-side rendering layer mask to filter which renderers a light affects — confirmed via [Light.renderingLayerMask](https://docs.unity3d.com/ScriptReference/Light-renderingLayerMask.html).

## Custom GI hooks (Experimental)

- [Experimental.GlobalIllumination.LightDataGI](https://docs.unity3d.com/ScriptReference/Experimental.GlobalIllumination.LightDataGI.html) — struct feeding custom light data into a GI baking backend; page marks it **Experimental** ("might be changed or removed in the future"). Key fields: `color`, `indirectColor`, `position`, `orientation`, `range`, `type`, `mode`, `coneAngle`, `innerConeAngle`, `shape0`, `shape1`, `falloff`, `cookieTextureEntityId`, `cookieScale`, `entityId`, `shadow`; methods `Init()`, `InitNoBake()`.
- [Rendering.SphericalHarmonicsL2](https://docs.unity3d.com/ScriptReference/Rendering.SphericalHarmonicsL2.html) — struct for second-order spherical harmonics (3 bands, 9 coefficients) used to represent probe/ambient lighting. Not marked experimental/deprecated. Key members: indexer `this[int,int]`, `AddAmbientLight()`, `AddDirectionalLight()`, `Clear()`, `Evaluate()`, operators `*`/`+`/`==`/`!=`.

## URP package API — per-light & pipeline asset

- [UniversalAdditionalLightData](https://docs.unity3d.com/Packages/com.unity.render-pipelines.universal@17.3/api/UnityEngine.Rendering.Universal.UniversalAdditionalLightData.html) — URP's per-light extension component (added automatically alongside `Light`). Key members: `lightCookieSize`, `lightCookieOffset`, `usePipelineSettings`, `softShadowQuality`, `customShadowLayers`, `shadowRenderingLayers`, `renderingLayers`, `additionalLightsShadowResolutionTier`.
- [UniversalRenderPipelineAsset](https://docs.unity3d.com/Packages/com.unity.render-pipelines.universal@17.3/api/UnityEngine.Rendering.Universal.UniversalRenderPipelineAsset.html) — the URP pipeline asset/quality-level object. Key lighting/shadow members: `shadowDistance`, `shadowCascadeCount`, `mainLightRenderingMode`, `supportsMainLightShadows`, `additionalLightsRenderingMode`, `additionalLightsShadowmapResolution`, `supportsMixedLighting`, `supportsSoftShadows`, `shadowDepthBias`, `shadowNormalBias`.

## URP/SRP Core package API — Adaptive Probe Volumes

- [ProbeVolume](https://docs.unity3d.com/Packages/com.unity.render-pipelines.core@17.3/api/UnityEngine.Rendering.ProbeVolume.html) — marker component (in `UnityEngine.Rendering`, part of the SRP Core package, used by both URP and HDRP) defining what area of a scene the Adaptive Probe Volumes system considers. Key members: `mode` (Global/Local), `size`, `objectLayerMask`, `fillEmptySpaces`, `overridesSubdivLevels` with `lowestSubdivLevelOverride`/`highestSubdivLevelOverride`, `minRendererVolumeSize`; methods `GetExtents()`, `GetVolume()`.
  Note: the SRP Core API index page (`.../com.unity.render-pipelines.core@17.3/api/index.html`) does not render a browsable class listing via fetch, so no other `Probe*` classes (e.g. a distinct `ProbeReferenceVolume`) could be independently confirmed from the index — `ProbeVolume` itself was confirmed directly via its own page.
