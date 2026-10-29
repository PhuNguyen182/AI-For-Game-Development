# Rendering Layers (light side)

Docs: Manual `urp/rendering-layers` ("Enable Rendering Layers for Lights"); API `RenderingLayerMask`. `unity-urp-rendering` owns the Decal/Renderer Feature side.

The culling mask does not scope the shadow pass: an object excluded by culling mask can still cast a shadow from that light (the giveaway symptom). Rendering Layers do.

- Asset toggle: must be enabled on the pipeline Asset first; until then the fields are editable and inert.
- `RenderingLayerMask`: 32-bit; names come from project settings, so keep masks set by index in code in step with masks set by name in the Inspector.
- `Light.renderingLayerMask`: which renderers the light affects and, under an SRP, renders into its shadow pass.
- `Renderer.renderingLayerMask`: the other half. A renderer left on the default layer is affected by every light.
- `customShadowLayers` on `UniversalAdditionalLightData`: an object can be lit without casting, or cast without being lit.
- APV: the same masks separate which lights a probe region samples ([probe-volumes.md](probe-volumes.md)).

Use only for genuine per-light exclusion (interior light must not reach the street). A layout or placement fix is usually cheaper than a mask scheme (KISS).
