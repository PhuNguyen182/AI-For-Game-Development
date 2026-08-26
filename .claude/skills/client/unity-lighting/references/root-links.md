# Root Links — Lighting Documentation Roots

Source: the Unity Manual and Scripting API roots listed below, plus the SRP
package API at `@17.6`.
Covers: SKILL.md §4 — **"Confirm the pipeline and then confirm which asset actually owns the setting being changed"**.

Lighting is split across two authorities that look identical in the Inspector:
the Built-in pipeline reads Quality Settings and `RenderSettings`, while URP
reads its own pipeline Asset for the same concepts. A change made to the
wrong one is accepted, saved, and has no effect, which is why the ownership
table below comes before any page link.

| Root | Holds | Source |
|---|---|---|
| Manual — Lighting | Light sources, direct and indirect lighting, shadows, reflections, Light Explorer, optimization | [Lighting](https://docs.unity3d.com/Manual/LightingOverview.html) |
| Manual — Lighting reference | Lighting window, Lighting Settings Asset, Lightmap Parameters, GI debug draw modes | [Lighting reference](https://docs.unity3d.com/Manual/lighting-reference.html) |
| Manual — URP lighting | URP light limits, per-light extension data, URP shadow and reflection pages, APV, Rendering Layers | [Lighting in URP](https://docs.unity3d.com/Manual/urp/lighting-landing.html) |
| API — `Light` | Every per-light parameter and its runtime behaviour | [Light](https://docs.unity3d.com/ScriptReference/Light.html) |
| API — `RenderSettings` | Scene-wide ambient, skybox, fog, and reflection intensity that feed indirect lighting | [RenderSettings](https://docs.unity3d.com/ScriptReference/RenderSettings.html) |
| API — SRP core and URP | `ProbeVolume`, `ProbeAdjustmentVolume`, `UniversalAdditionalLightData`, `UniversalRenderPipelineAsset` | [core RP 17.6](https://docs.unity3d.com/Packages/com.unity.render-pipelines.core@17.6/api/index.html) |

## Which asset owns which setting

| Setting | Built-in pipeline | URP | Source |
|---|---|---|---|
| Shadow distance, cascade count and splits | `QualitySettings.shadowDistance`, `shadowCascades`, `shadowCascade2Split`/`4Split` | `UniversalRenderPipelineAsset.shadowDistance`, `shadowCascadeCount`, `cascade2Split`–`cascade4Split` | [UniversalRenderPipelineAsset](https://docs.unity3d.com/Packages/com.unity.render-pipelines.universal@17.6/api/UnityEngine.Rendering.Universal.UniversalRenderPipelineAsset.html) |
| Shadow resolution | `QualitySettings.shadowResolution`, per-light `Light.shadowCustomResolution` | `mainLightShadowmapResolution`, `additionalLightsShadowmapResolution`, plus three per-light tiers on the Asset | [UniversalRenderPipelineAsset](https://docs.unity3d.com/Packages/com.unity.render-pipelines.universal@17.6/api/UnityEngine.Rendering.Universal.UniversalRenderPipelineAsset.html) |
| Per-light extras — shadow tier, soft shadow quality, custom shadow layers | Not present | `UniversalAdditionalLightData`, added automatically beside the `Light` | [UniversalAdditionalLightData](https://docs.unity3d.com/Packages/com.unity.render-pipelines.universal@17.6/api/UnityEngine.Rendering.Universal.UniversalAdditionalLightData.html) |
| Shadowmask mode | `QualitySettings.shadowmaskMode` — Shadowmask or Distance Shadowmask | Same Quality Settings field, still read under URP | [QualitySettings](https://docs.unity3d.com/ScriptReference/QualitySettings.html) |
| Ambient, skybox, fog | `RenderSettings` and the Lighting window's Environment tab | Same — these are not duplicated onto the URP Asset | [RenderSettings](https://docs.unity3d.com/ScriptReference/RenderSettings.html) |
| Adaptive Probe Volumes available at all | Not supported | A toggle on the pipeline Asset — set here on URP, owned by `unity-hdrp-rendering` on HDRP | [Adaptive Probe Volumes](https://docs.unity3d.com/Manual/urp/probevolumes.html) |

## Version pin

Manual and Scripting API links here are unversioned, which resolves to the
current documentation set rather than a pinned Editor version; SRP package
pages are pinned to `@17.6`. Any default value quoted in this folder was read
at the time of writing — confirm a specific number against the installed
Editor before relying on it, and swap the `@17.6` segment if the project
installs a different SRP version.

## Legacy slugs

| Old slug | Resolves to | Source |
|---|---|---|
| `Manual/GlobalIllumination.html` | The Lighting window reference — an old bookmark still lands correctly | [Lighting window](https://docs.unity3d.com/Manual/lighting-window.html) |
