# Light Sources & Parameters

Covers the Light-sources branch of the Manual: light types (Directional, Point, Spot, Area), the Light component and its Inspector parameters, ambient light from the environment, cookies, emissive materials as a light source, and the `UnityEngine.Light` Scripting API surface behind all of it.

## Manual
- [Light sources](https://docs.unity3d.com/Manual/lighting-light-sources.html)
- [Light components](https://docs.unity3d.com/Manual/lighting-light-components.html)
- [Types of Light component](https://docs.unity3d.com/Manual/Lighting.html)
- [Place Light components](https://docs.unity3d.com/Manual/UsingLights.html)
- [Per-pixel and per-vertex lights](https://docs.unity3d.com/Manual/PerPixelLights.html)
- [Light component Inspector window reference for the Built-In Render Pipeline](https://docs.unity3d.com/Manual/class-Light.html)
- [Add ambient light from the environment](https://docs.unity3d.com/Manual/lighting-ambient-light.html)
- [Cookies](https://docs.unity3d.com/Manual/Cookies.html)
- [Introduction to cookies](https://docs.unity3d.com/Manual/Cookies-introduction.html)
- [Apply a cookie](https://docs.unity3d.com/Manual/Cookies-apply.html)
- [Create cookies in the Built-In Render Pipeline](https://docs.unity3d.com/Manual/creating-cookies-built-in-render-pipeline.html)
- [Emit light from a GameObject in the Built-In Render Pipeline (emissive materials)](https://docs.unity3d.com/Manual/lighting-emissive-materials.html)
- [Search and explore lighting-related objects (Light Explorer)](https://docs.unity3d.com/Manual/LightingExplorer-landing.html)
- [Light Explorer window](https://docs.unity3d.com/Manual/LightingExplorer.html)
- [Lighting Search window reference](https://docs.unity3d.com/Manual/lighting-search-reference.html)

## Scripting API
- [Light](https://docs.unity3d.com/ScriptReference/Light.html) — the component itself.
- [Light.type](https://docs.unity3d.com/ScriptReference/Light-type.html) / [LightType](https://docs.unity3d.com/ScriptReference/LightType.html) — `Directional`, `Point`, `Spot`, `Rectangle`, `Disc`, `Pyramid`, `Box`, `Tube`.
- [Light.shadows](https://docs.unity3d.com/ScriptReference/Light-shadows.html) / [LightShadows](https://docs.unity3d.com/ScriptReference/LightShadows.html) — `None`, `Hard`, `Soft`.
- [Light.renderMode](https://docs.unity3d.com/ScriptReference/Light-renderMode.html) / [LightRenderMode](https://docs.unity3d.com/ScriptReference/LightRenderMode.html) — `Auto`, `ForcePixel`, `ForceVertex`.
- [LightShape](https://docs.unity3d.com/ScriptReference/LightShape.html) — obsolete; use `LightType.Spot`/`Pyramid`/`Box` instead.
- [Light.cookie](https://docs.unity3d.com/ScriptReference/Light-cookie.html) / [Light.cookieSize2D](https://docs.unity3d.com/ScriptReference/Light-cookieSize2D.html)
- [Light.range](https://docs.unity3d.com/ScriptReference/Light-range.html) / [Light.dilatedRange](https://docs.unity3d.com/ScriptReference/Light-dilatedRange.html)
- [Light.intensity](https://docs.unity3d.com/ScriptReference/Light-intensity.html) / [Light.bounceIntensity](https://docs.unity3d.com/ScriptReference/Light-bounceIntensity.html) / [Light.lightUnit](https://docs.unity3d.com/ScriptReference/Light-lightUnit.html) / [Light.luxAtDistance](https://docs.unity3d.com/ScriptReference/Light-luxAtDistance.html)
- [Light.color](https://docs.unity3d.com/ScriptReference/Light-color.html) / [Light.colorTemperature](https://docs.unity3d.com/ScriptReference/Light-colorTemperature.html) / [Light.useColorTemperature](https://docs.unity3d.com/ScriptReference/Light-useColorTemperature.html)
- [Light.cullingMask](https://docs.unity3d.com/ScriptReference/Light-cullingMask.html) / [Light.renderingLayerMask](https://docs.unity3d.com/ScriptReference/Light-renderingLayerMask.html)
- [Light.spotAngle](https://docs.unity3d.com/ScriptReference/Light-spotAngle.html) / [Light.innerSpotAngle](https://docs.unity3d.com/ScriptReference/Light-innerSpotAngle.html) / [Light.enableSpotReflector](https://docs.unity3d.com/ScriptReference/Light-enableSpotReflector.html)
- [Light.areaSize](https://docs.unity3d.com/ScriptReference/Light-areaSize.html) / [Light.shapeRadius](https://docs.unity3d.com/ScriptReference/Light-shapeRadius.html)
- [Light.lightmapBakeType](https://docs.unity3d.com/ScriptReference/Light-lightmapBakeType.html) / [LightmapBakeType](https://docs.unity3d.com/ScriptReference/LightmapBakeType.html) — `Realtime`, `Baked`, `Mixed`.
- [Light.bakingOutput](https://docs.unity3d.com/ScriptReference/Light-bakingOutput.html)
- Shadow-related: [Light.shadowStrength](https://docs.unity3d.com/ScriptReference/Light-shadowStrength.html), [Light.shadowBias](https://docs.unity3d.com/ScriptReference/Light-shadowBias.html), [Light.shadowNormalBias](https://docs.unity3d.com/ScriptReference/Light-shadowNormalBias.html), [Light.shadowNearPlane](https://docs.unity3d.com/ScriptReference/Light-shadowNearPlane.html), [Light.shadowResolution](https://docs.unity3d.com/ScriptReference/Light-shadowResolution.html), [Light.shadowCustomResolution](https://docs.unity3d.com/ScriptReference/Light-shadowCustomResolution.html), [Light.shadowAngle](https://docs.unity3d.com/ScriptReference/Light-shadowAngle.html)
- [Light.flare](https://docs.unity3d.com/ScriptReference/Light-flare.html)
- Command buffers: [Light.AddCommandBuffer](https://docs.unity3d.com/ScriptReference/Light.AddCommandBuffer.html), [Light.AddCommandBufferAsync](https://docs.unity3d.com/ScriptReference/Light.AddCommandBufferAsync.html), [Light.GetCommandBuffers](https://docs.unity3d.com/ScriptReference/Light.GetCommandBuffers.html), [Light.RemoveCommandBuffer](https://docs.unity3d.com/ScriptReference/Light.RemoveCommandBuffer.html), [Light.RemoveAllCommandBuffers](https://docs.unity3d.com/ScriptReference/Light.RemoveAllCommandBuffers.html)
- [RenderSettings](https://docs.unity3d.com/ScriptReference/RenderSettings.html) — scene-wide `ambientLight`, `ambientIntensity`, `ambientMode`, `ambientSkyColor`/`ambientEquatorColor`/`ambientGroundColor`, `ambientProbe`, `skybox`, `reflectionIntensity`, `reflectionBounces`, and fog (`fog`, `fogColor`, `fogMode`, `fogDensity`).
