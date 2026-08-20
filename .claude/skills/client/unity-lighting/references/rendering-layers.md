# Rendering Layers in URP

Covers URP Rendering Layers: enabling them for Lights and Decals, and using rendering layer masks to control which Lights/Decals affect which Renderers.

## Manual
- [Rendering Layers in URP](https://docs.unity3d.com/Manual/urp/features/rendering-layers.html)
- [Introduction to Rendering Layers in URP](https://docs.unity3d.com/Manual/urp/features/rendering-layers-introduction.html)
- [Enable Rendering Layers for Lights in URP](https://docs.unity3d.com/Manual/urp/features/rendering-layers-lights.html)
- [Enable Rendering Layers for Decals in URP](https://docs.unity3d.com/Manual/urp/features/rendering-layers-decals.html)
- [Prevent light leaks with rendering layer masks](https://docs.unity3d.com/Manual/urp/features/rendering-layer-masks-apv-landing.html)

## Scripting API
- [Class RenderingLayerMask](https://docs.unity3d.com/ScriptReference/RenderingLayerMask.html) — `UnityEngine.RenderingLayerMask`, a struct representing a bitmask over 32 rendering layers, used so Lights or effects affect only specific Renderers.
- [Light.renderingLayerMask](https://docs.unity3d.com/ScriptReference/Light-renderingLayerMask.html) — determines which rendering layer mask a Light affects; with a Scriptable Render Pipeline this filters Renderers during shadow passes by matching against the Renderer's rendering layer mask.
- [Renderer.renderingLayerMask](https://docs.unity3d.com/ScriptReference/Renderer-renderingLayerMask.html) — a `uint` property determining which rendering layer a Renderer lives on when using a Scriptable Render Pipeline.
