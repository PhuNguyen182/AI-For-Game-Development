# DOTS Instancing Shaders & Material Overrides

Covers SKILL.md steps 5 and 6 — shader compatibility, then the two ways to override a material property per entity.

## Manual — DOTS Instancing
- [DOTS Instancing Shader](https://docs.unity3d.com/Packages/com.unity.entities.graphics@6.6/manual/dots-instancing-shader.html) — "to render entities with Entities Graphics, shaders must be DOTS Instancing compatible." Built-in URP/HDRP shaders already support it with no changes. A Shader Graph gets DOTS Instancing compatibility for its custom properties by implementing material overrides (below). Hand-written shaders need to follow the package's sample custom unlit shader's pattern.

## Manual — Material Overrides
- [Material Overrides](https://docs.unity3d.com/Packages/com.unity.entities.graphics@6.6/manual/material-overrides.html) — overriding HDRP/URP material property values (or a custom Shader Graph's) per entity, via two approaches: C#/Burst code, or a Material Override Asset. Sample scenes exist for both, per-pipeline, in `HDRPSamples`/`URPSamples`.
- [Material Overrides Using C#](https://docs.unity3d.com/Packages/com.unity.entities.graphics@6.6/manual/material-overrides-code.html) — two flavors: (1) built-in overrides — add pre-built `IComponentData` like `BaseColor`/`Metallic`/`Smoothness` directly; (2) custom Shader Graph overrides — mark the Shader Graph property "Hybrid Per Instance" in Node Settings, then define a matching struct: `[MaterialProperty("_Color")] public struct MyOwnColor : IComponentData { public float4 Value; }`, and write a Burst system updating it via `SystemAPI.Query<RefRW<T>>()`. A matching `IComponentData` struct is required for every "Hybrid Per Instance" property.
- [Material Overrides Using an Asset](https://docs.unity3d.com/Packages/com.unity.entities.graphics@6.6/manual/material-overrides-asset.html) — no-code path: `Assets > Create > Shader > Material Override Asset`, assign a material, click "Add Property Override" to pick properties (for Shader Graph materials, enable "Override Property Declaration" → "Hybrid Per Instance"), set values, then add a Material Override component to a GameObject referencing the asset. Properties can be edited at the asset level (affects everyone) or per-GameObject instance (shown with blue margins/bold text in the Inspector).

Choose C#/Burst when the value needs to be computed/animated/systemic; choose the asset when it's a fixed, designer-facing per-instance tweak with no code — see SKILL.md step 6.
