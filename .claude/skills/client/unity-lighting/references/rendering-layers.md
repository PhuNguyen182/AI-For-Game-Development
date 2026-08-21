# Rendering Layers — Scoping Lights to Renderers

Sources: [Rendering Layers in URP](https://docs.unity3d.com/Manual/urp/features/rendering-layers.html), [Enable Rendering Layers for Lights](https://docs.unity3d.com/Manual/urp/features/rendering-layers-lights.html), [RenderingLayerMask API](https://docs.unity3d.com/ScriptReference/RenderingLayerMask.html).
Covers: SKILL.md §4 — **"Scope lights with Rendering Layers rather than culling masks under an SRP"**.

Rendering Layers are the SRP-era answer to "this light should not touch that
object". They replace the culling mask for this purpose because the culling
mask does not scope the shadow pass — an object excluded from a light by
culling mask can still cast a shadow from it, which is the giveaway symptom.
`unity-urp-rendering` owns the same feature from the Decal and Renderer
Feature side; this file is strictly the light-to-renderer masking use.

| Piece | What it decides | Source |
|---|---|---|
| The Asset toggle | Rendering Layers must be enabled on the pipeline Asset before any mask is honoured. Until then the fields are editable and inert | [Enable Rendering Layers for Lights](https://docs.unity3d.com/Manual/urp/features/rendering-layers-lights.html) |
| `RenderingLayerMask` | A 32-bit mask; the names come from project settings, so a mask set by index in code and a mask set by name in the Inspector must be kept in step | [RenderingLayerMask](https://docs.unity3d.com/ScriptReference/RenderingLayerMask.html) |
| `Light.renderingLayerMask` | Which renderers this light affects, and — under an SRP — which ones it renders into its shadow pass | [Light.renderingLayerMask](https://docs.unity3d.com/ScriptReference/Light-renderingLayerMask.html) |
| `Renderer.renderingLayerMask` | The other half of the match. A renderer left on the default layer is affected by every light regardless of how carefully the lights were masked | [Renderer.renderingLayerMask](https://docs.unity3d.com/ScriptReference/Renderer-renderingLayerMask.html) |
| `customShadowLayers` on `UniversalAdditionalLightData` | Lets shadow casters differ from lit objects for one light — an object can be lit without casting, or cast without being lit | [UniversalAdditionalLightData](https://docs.unity3d.com/Packages/com.unity.render-pipelines.universal@17.6/api/UnityEngine.Rendering.Universal.UniversalAdditionalLightData.html) |
| APV leak prevention | The same masks separate which lights an Adaptive Probe Volume region samples — see [probe-volumes.md](probe-volumes.md) | [Prevent light leaks with rendering layer masks](https://docs.unity3d.com/Manual/urp/features/rendering-layer-masks-apv-landing.html) |

Reach for this when a scene genuinely needs per-light exclusion — an interior
light that must not reach the street, an exterior sun that must not enter a
room's probe data. A scene-layout fix or a simpler light placement is usually
cheaper to maintain than a mask scheme spread across lights and renderers,
per KISS in `coding-principles.md`.
