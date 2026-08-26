# Shadows — Distance, Cascades, Bias, Resolution

Sources: [Shadows](https://docs.unity3d.com/Manual/Shadows.html), [Shadow cascades](https://docs.unity3d.com/Manual/shadow-cascades.html), [Set shadow distance](https://docs.unity3d.com/Manual/shadow-distance.html), [Troubleshooting shadows](https://docs.unity3d.com/Manual/ShadowPerformance.html), [Shadows in URP](https://docs.unity3d.com/Manual/urp/Shadows-in-URP.html).
Covers: SKILL.md §4 — **"Spend shadow budget on distance before resolution"**, **"Fix shadow acne with normal bias before depth bias"**.

Shadow cost is dominated by how much world the shadow map has to cover, not by
how many texels it has. That single relationship explains why raising
resolution rarely fixes a soft or blocky shadow while lowering distance
usually does, and why cascades — which subdivide the covered distance rather
than extending it — are a redistribution, not an increase.

## Contents

- [Distance and cascades](#distance-and-cascades)
- [Bias](#bias)
- [Resolution](#resolution)
- [URP per-light settings](#urp-per-light-settings)

## Distance and cascades

| Setting | What it decides | Source |
|---|---|---|
| Shadow distance | The radius from the camera within which realtime shadows exist at all. Halving it roughly quarters the world area one shadow map covers, which is why it is the first lever | [Set shadow distance](https://docs.unity3d.com/Manual/shadow-distance.html) |
| Cascade count | Splits that same distance into 2 or 4 nested regions, each with its own map, so near geometry gets more texels per metre. **Does not extend reach** — a scene wanting shadows further away needs distance, not cascades | [Introduction to shadow cascades](https://docs.unity3d.com/Manual/shadow-cascades.html) |
| Cascade splits | Where the boundaries fall as fractions of the distance. Defaults suit a ground-level camera; a top-down or long-sightline game usually wants them redistributed | [Configure shadow cascades](https://docs.unity3d.com/Manual/shadow-cascades-use.html) |
| Cascade border / fade | The blend band at the outermost edge. Too narrow and the shadow cut-off is a visible line across the ground | [UniversalRenderPipelineAsset](https://docs.unity3d.com/Packages/com.unity.render-pipelines.universal@17.6/api/UnityEngine.Rendering.Universal.UniversalRenderPipelineAsset.html) |
| Cost | Each cascade is another render of the shadow casters it contains — four cascades is closer to four shadow passes than to one | [Performance impact of shadow cascades](https://docs.unity3d.com/Manual/shadow-cascades-performance.html) |
| Cascades apply to | Directional lights only. Point and spot lights get one map each, and a point light's is a cube | [Introduction to shadow cascades](https://docs.unity3d.com/Manual/shadow-cascades.html) |

## Bias

Two artifacts, opposite causes, and one of the two fixes creates the other.

| Symptom | Cause and correct lever | Source |
|---|---|---|
| Shadow acne — striped self-shadowing on lit surfaces | The surface shadows itself through shadow-map precision. **Normal bias** offsets the sample along the surface normal and is the first lever, because it barely disturbs contact | [Troubleshooting shadows](https://docs.unity3d.com/Manual/ShadowPerformance.html) |
| Peter-panning — the shadow detaches and the object appears to float | Too much **depth bias**, which pushed the whole comparison along the light ray. Reduce it and take the remaining acne on normal bias instead | [Troubleshooting shadows](https://docs.unity3d.com/Manual/ShadowPerformance.html) |
| Acne that no bias value fixes | Usually resolution or distance, not bias — the map has too few texels for the covered area, and biasing further only trades one artifact for the other | [Troubleshooting shadows in URP](https://docs.unity3d.com/Manual/urp/shadows-troubleshooting-urp.html) |
| `shadowNearPlane` | The near clip of the shadow projection; raising it recovers precision for a scene whose casters are all far from the light | [Light API](https://docs.unity3d.com/ScriptReference/Light.html) |

## Resolution

| Setting | What it decides | Source |
|---|---|---|
| `mainLightShadowmapResolution` | The directional light's map, split across its cascades — a 2048 map with four cascades gives each 1024 | [UniversalRenderPipelineAsset](https://docs.unity3d.com/Packages/com.unity.render-pipelines.universal@17.6/api/UnityEngine.Rendering.Universal.UniversalRenderPipelineAsset.html) |
| `additionalLightsShadowmapResolution` | One atlas shared by every shadow-casting point and spot light. More casters means smaller slices, not a larger atlas | [UniversalRenderPipelineAsset](https://docs.unity3d.com/Packages/com.unity.render-pipelines.universal@17.6/api/UnityEngine.Rendering.Universal.UniversalRenderPipelineAsset.html) |
| Low / Medium / High tiers | Three named slice sizes on the URP Asset that each additional light then selects from, rather than each light naming a resolution | [Configure shadow resolution in URP](https://docs.unity3d.com/Manual/urp/shadow-resolution-urp.html) |
| `supportsSoftShadows` | A pipeline-wide gate. With it off, a light set to Soft Shadows renders hard ones and says nothing | [UniversalRenderPipelineAsset](https://docs.unity3d.com/Packages/com.unity.render-pipelines.universal@17.6/api/UnityEngine.Rendering.Universal.UniversalRenderPipelineAsset.html) |
| `conservativeEnclosingSphere` | Fixes shadow culling artifacts at cascade edges where casters pop out. Off by default for backward compatibility, so an existing project must opt in | [UniversalRenderPipelineAsset](https://docs.unity3d.com/Packages/com.unity.render-pipelines.universal@17.6/api/UnityEngine.Rendering.Universal.UniversalRenderPipelineAsset.html) |
| Screen space shadows | An extra full-screen pass in URP; worth it only where the shadow map resolution alone cannot deliver the contact quality wanted | [Screen space shadows](https://docs.unity3d.com/Manual/urp/renderer-feature-screen-space-shadows.html) |

## URP per-light settings

| Member on `UniversalAdditionalLightData` | What it decides | Source |
|---|---|---|
| `additionalLightsShadowResolutionTier` | Which of the three Asset tiers this light draws into | [UniversalAdditionalLightData](https://docs.unity3d.com/Packages/com.unity.render-pipelines.universal@17.6/api/UnityEngine.Rendering.Universal.UniversalAdditionalLightData.html) |
| `usePipelineSettings` | Whether the light takes the Asset's bias values or its own — the reason a per-light bias edit sometimes appears to do nothing | [UniversalAdditionalLightData](https://docs.unity3d.com/Packages/com.unity.render-pipelines.universal@17.6/api/UnityEngine.Rendering.Universal.UniversalAdditionalLightData.html) |
| `softShadowQuality` | Per-light soft shadow filtering quality, independent of the pipeline-wide toggle above it | [UniversalAdditionalLightData](https://docs.unity3d.com/Packages/com.unity.render-pipelines.universal@17.6/api/UnityEngine.Rendering.Universal.UniversalAdditionalLightData.html) |
| `customShadowLayers` / `shadowRenderingLayers` | Lets a light's shadow casters differ from the objects it lights — see [rendering-layers.md](rendering-layers.md) | [UniversalAdditionalLightData](https://docs.unity3d.com/Packages/com.unity.render-pipelines.universal@17.6/api/UnityEngine.Rendering.Universal.UniversalAdditionalLightData.html) |

Visualising the cascade split in the Scene view is the fastest way to confirm
splits match the level's real sightlines rather than the template defaults —
see [Visualize shadow cascades](https://docs.unity3d.com/Manual/urp/shadow-cascades-visualize.html).
