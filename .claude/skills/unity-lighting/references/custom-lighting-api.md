# URP Lighting HLSL

Docs: Manual `urp` pages "Custom lighting in URP", "Use lighting in a custom URP shader", "Render additional lights", "Use indirect lighting", "Change light falloff", "Convert custom shaders for URP". The shader itself (and a Built-in conversion): `shader-authoring`.

| Entry point | Does |
|---|---|
| `GetMainLight()` | Main directional `Light` struct: direction, colour, attenuation |
| `GetAdditionalLightsCount()` + `GetAdditionalLight()` | Iterate non-main lights. Under Forward+ write the loop between `LIGHT_LOOP_BEGIN` and `LIGHT_LOOP_END` so the shader works across rendering paths |
| `LightingLambert()` / `LightingSpecular()` | Built-in diffuse/specular evaluation |
| `DistanceAttenuation()` / `AngleAttenuation()` | Hooks for a custom falloff curve |
| `SampleSH()` | Ambient spherical-harmonic baseline indirect |
| `EvaluateAdaptiveProbeVolume()` | Reads APV data ([probe-volumes.md](probe-volumes.md)) |
| `GlossyEnvironmentReflection()` | Reflection Probe contribution by smoothness ([reflections.md](reflections.md)) |

Structs: `Light`, `InputData`, `AmbientOcclusionFactor`, plus the shader's `Attributes`/`Varyings`.

| Include | For |
|---|---|
| `com.unity.render-pipelines.universal/ShaderLibrary/Lighting.hlsl` | Main entry points and structs |
| `.../ShaderLibrary/RealtimeLights.hlsl` | Additional-light iteration, loop macros |
| `.../ShaderLibrary/GlobalIllumination.hlsl` | Indirect and environment reflection |
| `.../ShaderLibrary/AmbientOcclusion.hlsl` | `AmbientOcclusionFactor` |
| `com.unity.render-pipelines.core/Runtime/Lighting/ProbeVolume/ProbeVolume.hlsl` | APV evaluation |
| `com.unity.render-pipelines.core/ShaderLibrary/AmbientProbe.hlsl` | Ambient probe sampling |
