# Direct/Indirect Lighting & Global Illumination

Covers the Direct-and-indirect-lighting branch of the Manual: Baked GI vs. Realtime GI (Enlighten) vs. Mixed lighting, Lighting Modes (Baked Indirect, Shadowmask, Subtractive), the Progressive Lightmapper, the Lighting window, Light Probes, and lightmap UVs/data — plus the Scripting API classes behind baking and probe/lightmap data.

## Manual
- [Direct and indirect lighting](https://docs.unity3d.com/Manual/direct-and-indirect-lighting.html)
- [Global Illumination](https://docs.unity3d.com/Manual/lighting-window.html) *(the `GlobalIllumination.html` slug now redirects here — see note below)*
- [Choose a lighting setup / Global illumination overview](https://docs.unity3d.com/Manual/choose-a-lighting-setup.html)
- [Lighting window reference](https://docs.unity3d.com/Manual/lighting-window.html)
- [Precalculating surface lighting with lightmaps](https://docs.unity3d.com/Manual/Lightmapping-landing.html)
- [Baking lightmaps before runtime](https://docs.unity3d.com/Manual/Lightmapping-baking-before-runtime.html)
- [Lightmaps and baking](https://docs.unity3d.com/Manual/Lightmappers.html)
- [Set up your scene and lights for baking](https://docs.unity3d.com/Manual/Lightmapping.html)
- [Bake lighting](https://docs.unity3d.com/Manual/Lightmapping-bake.html)
- [Configuring baking lightmaps](https://docs.unity3d.com/Manual/Lightmapping-configure.html)
- [Optimize baked lightmaps (Progressive Lightmapper / GPU)](https://docs.unity3d.com/Manual/GPUProgressiveLightmapper.html)
- [Troubleshooting baked lightmaps](https://docs.unity3d.com/Manual/Lightmapping-troubleshooting.html)
- [Lightmapping settings in the Lighting Settings Asset reference](https://docs.unity3d.com/Manual/Lightmaps-reference.html)
- [Update lightmaps at runtime with Enlighten Realtime Global Illumination](https://docs.unity3d.com/Manual/realtime-gi-using-enlighten-landing.html)
- [Realtime Global Illumination using Enlighten](https://docs.unity3d.com/Manual/realtime-gi-using-enlighten.html)
- [Enable Enlighten Realtime Global Illumination](https://docs.unity3d.com/Manual/realtime-gi-using-enlighten-use.html)
- [Optimize Enlighten Realtime Global Illumination](https://docs.unity3d.com/Manual/realtime-gi-using-enlighten-optimize.html)
- [Light Modes (Baked / Realtime / Mixed introduction)](https://docs.unity3d.com/Manual/LightModes-introduction.html)
- [Choose a Light Mode](https://docs.unity3d.com/Manual/LightModes-choose.html)
- [Configuring Mixed lights with Lighting Modes (Baked Indirect, Shadowmask, Subtractive)](https://docs.unity3d.com/Manual/lighting-mode.html)
- [Set the Lighting Mode of a scene](https://docs.unity3d.com/Manual/LightMode-Scene.html)
- [Lighting data](https://docs.unity3d.com/Manual/Lightmap-data-landing.html)
- [Lighting Data Assets](https://docs.unity3d.com/Manual/LightingDataAsset.html)
- [Precalculating indirect light with Light Probes](https://docs.unity3d.com/Manual/LightProbes-landing.html)
- [Introduction to Light Probes](https://docs.unity3d.com/Manual/LightProbes.html)
- [Place Light Probes with the Editor](https://docs.unity3d.com/Manual/class-LightProbeGroup.html)
- [Place Light Probes with a script](https://docs.unity3d.com/Manual/LightProbes-Placing-Scripting.html)
- [Set a GameObject to use light from Light Probes](https://docs.unity3d.com/Manual/LightProbes-MeshRenderer.html)
- [Light Probes and moving GameObjects](https://docs.unity3d.com/Manual/LightProbes-MovingObjects.html)
- [Light Probes reference](https://docs.unity3d.com/Manual/LightProbes-Reference.html)
- [Light Probe data format](https://docs.unity3d.com/Manual/LightProbes-TechnicalInformation.html)
- [Lightmap UVs](https://docs.unity3d.com/Manual/LightingGiUvs-landing.html)
- [Introduction to lightmap UVs](https://docs.unity3d.com/Manual/LightingGiUvs.html)
- [Generate lightmap UVs](https://docs.unity3d.com/Manual/LightingGiUvs-GeneratingLightmappingUVs.html)
- [Lightmap UVs Settings in the Model Import Settings Inspector window reference](https://docs.unity3d.com/Manual/LightingGiUvs-Reference.html)
- [Store light direction with Directional Mode](https://docs.unity3d.com/Manual/LightmappingDirectional.html)
- [Add ambient light from the environment (Skybox as a light source)](https://docs.unity3d.com/Manual/lighting-ambient-light.html)
- [Skyboxes](https://docs.unity3d.com/Manual/sky-landing.html)

Note: `Manual/GlobalIllumination.html` is a legacy slug that 301-redirects to `Manual/lighting-window.html` in the current Manual — kept above so both the old and current entry points are documented.

## Scripting API
- [Lightmapping](https://docs.unity3d.com/ScriptReference/Lightmapping.html) — editor-time bake control: `Bake()`, `BakeAsync()`, `BakeMultipleScenes()`, `BakeReflectionProbe()`, `Cancel()`, `Clear()`, `ClearDiskCache()`, `SetLightingSettingsForScene()`, plus `isRunning`, `buildProgress`, `lightingSettings`, `lightingDataAsset`, `bakeOnSceneLoad`.
- [LightmapSettings](https://docs.unity3d.com/ScriptReference/LightmapSettings.html) — `lightmaps`, `lightmapsMode`, `lightProbes`.
- [LightmapData](https://docs.unity3d.com/ScriptReference/LightmapData.html) — `lightmapColor`, `lightmapDir`, `shadowMask`.
- [LightProbes](https://docs.unity3d.com/ScriptReference/LightProbes.html) — `GetInterpolatedProbe`, `CalculateInterpolatedLightAndOcclusionProbes`, `GetSharedLightProbesForScene`, `GetInstantiatedLightProbesForScene`, `Tetrahedralize`, `TetrahedralizeAsync`.
- [LightProbeGroup](https://docs.unity3d.com/ScriptReference/LightProbeGroup.html) — component specifying where to bake a set of Light Probes.
- [Light.lightmapBakeType](https://docs.unity3d.com/ScriptReference/Light-lightmapBakeType.html) / [LightmapBakeType](https://docs.unity3d.com/ScriptReference/LightmapBakeType.html) — `Realtime`, `Baked`, `Mixed`.
- [MixedLightingMode](https://docs.unity3d.com/ScriptReference/MixedLightingMode.html) — `IndirectOnly`, `Shadowmask`, `Subtractive`.
- [RenderSettings](https://docs.unity3d.com/ScriptReference/RenderSettings.html) — scene-wide ambient/skybox/fog values that feed indirect lighting.
