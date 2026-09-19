# DOTS Instancing Compatibility & Material Overrides

Sources: [DOTS Instancing Shader](https://docs.unity3d.com/Packages/com.unity.entities.graphics@6.6/manual/dots-instancing-shader.html), [Material Overrides Using C#](https://docs.unity3d.com/Packages/com.unity.entities.graphics@6.6/manual/material-overrides-code.html), [Material Overrides Using an Asset](https://docs.unity3d.com/Packages/com.unity.entities.graphics@6.6/manual/material-overrides-asset.html).
Covers: SKILL.md §4 — **"Confirm DOTS Instancing compatibility before a custom shader reaches an entity"**, **"Choose the material-override mechanism by who has to change the value"**.

Whether a shader can render entities at all, and the two supported ways to vary
one of its properties per entity. The shader's own node logic belongs to
`shader-authoring`; only the compatibility contract lives here.

## Compatibility

| Shader | What it decides | Source |
|---|---|---|
| Built-in URP or HDRP shaders | Already DOTS Instancing compatible — no work required | [DOTS Instancing Shader](https://docs.unity3d.com/Packages/com.unity.entities.graphics@6.6/manual/dots-instancing-shader.html) |
| Custom Shader Graph | Gains compatibility for its own properties by implementing material overrides — compatibility is a consequence of the override setup, not a separate switch | [DOTS Instancing Shader](https://docs.unity3d.com/Packages/com.unity.entities.graphics@6.6/manual/dots-instancing-shader.html) |
| Hand-written shader | Must follow the package's sample custom unlit shader's pattern | [DOTS Instancing Shader](https://docs.unity3d.com/Packages/com.unity.entities.graphics@6.6/manual/dots-instancing-shader.html) |

## The two override mechanisms

| Mechanism | Use when | Source |
|---|---|---|
| Built-in override components (`BaseColor`, `Metallic`, `Smoothness`) | The property is one URP/HDRP already exposes — add the pre-built `IComponentData` and write it | [Overrides using C#](https://docs.unity3d.com/Packages/com.unity.entities.graphics@6.6/manual/material-overrides-code.html) |
| `[MaterialProperty("_Name")] IComponentData` | The value is computed, animated, or systemic; a Burst system writes it via `SystemAPI.Query<RefRW<T>>()` | [Overrides using C#](https://docs.unity3d.com/Packages/com.unity.entities.graphics@6.6/manual/material-overrides-code.html) |
| Material Override Asset | A designer sets a fixed per-instance value with no code — `Assets > Create > Shader > Material Override Asset`, then a Material Override component referencing it | [Overrides using an asset](https://docs.unity3d.com/Packages/com.unity.entities.graphics@6.6/manual/material-overrides-asset.html) |

```csharp
[MaterialProperty("_BaseColor")]
public struct TintOverride : IComponentData
{
    public float4 Value;
}
```

| Rule | What it decides | Source |
|---|---|---|
| Hybrid Per Instance declaration | A Shader Graph property must be marked Hybrid Per Instance in Node Settings before any override can reach it | [Overrides using C#](https://docs.unity3d.com/Packages/com.unity.entities.graphics@6.6/manual/material-overrides-code.html) |
| One struct per property | Every Hybrid Per Instance property needs its own matching `IComponentData` | [Overrides using C#](https://docs.unity3d.com/Packages/com.unity.entities.graphics@6.6/manual/material-overrides-code.html) |
| Asset-level versus instance-level editing | Editing the asset affects every user; per-GameObject edits show with blue margins and bold text in the Inspector | [Overrides using an asset](https://docs.unity3d.com/Packages/com.unity.entities.graphics@6.6/manual/material-overrides-asset.html) |

**Critical caveat**: the string in `[MaterialProperty]` must match the shader's
declared property name exactly. A mismatch produces no compile error, no
runtime warning, and no visible binding — the system writes a component that
nothing reads, which is why verification means watching the rendered result
change, not confirming the component is written.
