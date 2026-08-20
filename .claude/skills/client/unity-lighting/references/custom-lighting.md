# Custom Lighting in URP

Covers writing custom lit shaders against URP's lighting system: the built-in shader methods for direct/indirect lighting, light falloff, additional-light iteration, and converting Built-In shaders to URP.

## Manual
- [Custom lighting in URP](https://docs.unity3d.com/Manual/urp/lighting/custom-lighting-landing.html)
- [Introduction to custom lighting in URP](https://docs.unity3d.com/Manual/urp/lighting/custom-lighting-introduction.html)
- [Use lighting in a custom URP shader](https://docs.unity3d.com/Manual/urp/use-built-in-shader-methods-lighting.html)
- [Use indirect lighting in a custom URP shader](https://docs.unity3d.com/Manual/urp/use-built-in-shader-methods-indirect-lighting.html)
- [Render additional lights in a shader in URP](https://docs.unity3d.com/Manual/urp/use-built-in-shader-methods-additional-lights-fplus.html)
- [Change how lights fade using light falloff in URP](https://docs.unity3d.com/Manual/urp/lighting/custom-lighting-change-light-falloff.html)
- [Writing custom shaders in URP](https://docs.unity3d.com/Manual/urp/writing-custom-shaders-urp.html)
- [Modify URP source code](https://docs.unity3d.com/Manual/urp/customize/modify-urp-source-code.html)
- [Convert custom shaders for URP compatibility](https://docs.unity3d.com/Manual/urp/urp-shaders/birp-urp-custom-shader-upgrade-guide.html)

## Key HLSL entry points

Confirmed from fetched page content (not guessed):

- `GetMainLight()` — returns the main directional `Light` struct (`InputData`-driven), used in "Introduction to custom lighting" and "Use lighting in a custom URP shader".
- `GetAdditionalLight()` / `GetAdditionalLightsCount()` — iterate additional (non-main) lights, used in "Render additional lights in a shader in URP" inside a `LIGHT_LOOP_BEGIN` / `LIGHT_LOOP_END` loop.
- `LightingLambert()` / `LightingSpecular()` — built-in diffuse/specular lighting helper functions, from "Use lighting in a custom URP shader".
- `DistanceAttenuation()` / `AngleAttenuation()` — control light falloff by distance and spot angle, from "Change how lights fade using light falloff in URP".
- `GlossyEnvironmentReflection()` / `EvaluateAdaptiveProbeVolume()` / `SampleSH()` — indirect/ambient lighting and Adaptive Probe Volume sampling, from "Use indirect lighting in a custom URP shader".
- Structs: `InputData`, `Light`, `AmbientOcclusionFactor`, `Attributes`, `Varyings`.
- Include files referenced: `Packages/com.unity.render-pipelines.universal/ShaderLibrary/Lighting.hlsl`, `RealtimeLights.hlsl`, `AmbientOcclusion.hlsl`, `Packages/com.unity.render-pipelines.universal/ShaderLibrary/GlobalIllumination.hlsl`, `Packages/com.unity.render-pipelines.core/Runtime/Lighting/ProbeVolume/ProbeVolume.hlsl`, `Packages/com.unity.render-pipelines.core/ShaderLibrary/AmbientProbe.hlsl`.
