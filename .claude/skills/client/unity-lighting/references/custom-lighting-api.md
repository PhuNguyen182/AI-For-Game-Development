# URP Lighting HLSL — What a Custom Lit Shader Calls

Sources: [Custom lighting in URP](https://docs.unity3d.com/Manual/urp/lighting/custom-lighting-landing.html), [Use lighting in a custom URP shader](https://docs.unity3d.com/Manual/urp/use-built-in-shader-methods-lighting.html), [Render additional lights in a shader](https://docs.unity3d.com/Manual/urp/use-built-in-shader-methods-additional-lights-fplus.html), [Use indirect lighting in a custom URP shader](https://docs.unity3d.com/Manual/urp/use-built-in-shader-methods-indirect-lighting.html).
Covers: SKILL.md §4 — **"Supply the lighting API and hand the shader off"**.

The entry points below are what a hand-written URP lit shader must call to
receive the lights this skill configured. They are listed here so the lighting
setup and the shader agree; the shader itself is `shader-authoring`'s work.
Every function was read from the fetched Manual pages rather than recalled.

| Entry point | What it returns or does | Source |
|---|---|---|
| `GetMainLight()` | The main directional light as a `Light` struct — direction, colour, and attenuation together | [Use lighting in a custom URP shader](https://docs.unity3d.com/Manual/urp/use-built-in-shader-methods-lighting.html) |
| `GetAdditionalLightsCount()` and `GetAdditionalLight()` | Iterate the non-main lights. Under Forward+ the loop must be written between `LIGHT_LOOP_BEGIN` and `LIGHT_LOOP_END`, which is what makes the same shader work across rendering paths | [Render additional lights](https://docs.unity3d.com/Manual/urp/use-built-in-shader-methods-additional-lights-fplus.html) |
| `LightingLambert()` / `LightingSpecular()` | Built-in diffuse and specular evaluation, so a custom shader can restyle the result without reimplementing the model | [Use lighting in a custom URP shader](https://docs.unity3d.com/Manual/urp/use-built-in-shader-methods-lighting.html) |
| `DistanceAttenuation()` / `AngleAttenuation()` | Falloff by distance and by spot cone — the hooks for a non-default falloff curve | [Change light falloff](https://docs.unity3d.com/Manual/urp/lighting/custom-lighting-change-light-falloff.html) |
| `SampleSH()` | Ambient spherical-harmonic lighting, the baseline indirect term | [Use indirect lighting](https://docs.unity3d.com/Manual/urp/use-built-in-shader-methods-indirect-lighting.html) |
| `EvaluateAdaptiveProbeVolume()` | Reads Adaptive Probe Volume data — the shader-side counterpart of the APV setup in [probe-volumes.md](probe-volumes.md) | [Use indirect lighting](https://docs.unity3d.com/Manual/urp/use-built-in-shader-methods-indirect-lighting.html) |
| `GlossyEnvironmentReflection()` | Reflection Probe contribution for a given smoothness — how the probes placed in [reflections.md](reflections.md) reach a custom shader | [Use indirect lighting](https://docs.unity3d.com/Manual/urp/use-built-in-shader-methods-indirect-lighting.html) |

Structs the above exchange: `Light`, `InputData`, `AmbientOcclusionFactor`,
plus the shader's own `Attributes` and `Varyings`.

| Include file | Why it is needed | Source |
|---|---|---|
| `com.unity.render-pipelines.universal/ShaderLibrary/Lighting.hlsl` | The main lighting entry points and structs | [Use lighting in a custom URP shader](https://docs.unity3d.com/Manual/urp/use-built-in-shader-methods-lighting.html) |
| `.../ShaderLibrary/RealtimeLights.hlsl` | Additional-light iteration and the loop macros | [Render additional lights](https://docs.unity3d.com/Manual/urp/use-built-in-shader-methods-additional-lights-fplus.html) |
| `.../ShaderLibrary/GlobalIllumination.hlsl` | Indirect and environment reflection functions | [Use indirect lighting](https://docs.unity3d.com/Manual/urp/use-built-in-shader-methods-indirect-lighting.html) |
| `.../ShaderLibrary/AmbientOcclusion.hlsl` | `AmbientOcclusionFactor` and its sampling | [Use indirect lighting](https://docs.unity3d.com/Manual/urp/use-built-in-shader-methods-indirect-lighting.html) |
| `com.unity.render-pipelines.core/Runtime/Lighting/ProbeVolume/ProbeVolume.hlsl` | APV evaluation | [Use indirect lighting](https://docs.unity3d.com/Manual/urp/use-built-in-shader-methods-indirect-lighting.html) |
| `com.unity.render-pipelines.core/ShaderLibrary/AmbientProbe.hlsl` | Ambient probe sampling | [Use indirect lighting](https://docs.unity3d.com/Manual/urp/use-built-in-shader-methods-indirect-lighting.html) |

Converting an existing Built-in pipeline shader is a documented migration
rather than a rewrite — see [Convert custom shaders for URP](https://docs.unity3d.com/Manual/urp/urp-shaders/birp-urp-custom-shader-upgrade-guide.html),
and hand the conversion itself to `shader-authoring`.
