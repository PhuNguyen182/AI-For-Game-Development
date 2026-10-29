# DOTS Instancing and material overrides

Sources (under `manual/`): `dots-instancing-shader.html`, `material-overrides-code.html`, `material-overrides-asset.html`.

Shader node logic is `shader-authoring`; only the compatibility contract is here.

## Compatibility
| Shader | Status |
|---|---|
| Built-in URP/HDRP shaders | Already compatible |
| Custom Shader Graph | Gains compatibility for its own properties by implementing material overrides (not a separate switch) |
| Hand-written | Follow the package's sample custom unlit shader |

## Override mechanisms
| Mechanism | Use when |
|---|---|
| Built-in override components (`BaseColor`, `Metallic`, `Smoothness`) | URP/HDRP already exposes the property: add the pre-built `IComponentData` and write it |
| `[MaterialProperty("_Name")] IComponentData` | Value is computed or animated; a Burst system writes it via `SystemAPI.Query<RefRW<T>>()` |
| Material Override Asset | A designer sets a fixed per-instance value with no code: `Assets > Create > Shader > Material Override Asset`, then a Material Override component referencing it |

```csharp
[MaterialProperty("_BaseColor")]
public struct TintOverride : IComponentData { public float4 Value; }
```

- A Shader Graph property must be marked Hybrid Per Instance (Node Settings) before any override reaches it; each such property needs its own matching struct.
- The `[MaterialProperty]` string must equal the shader's declared name exactly; a mismatch gives no compile error, warning or binding.
- Asset-level edits affect every user; per-GameObject edits show blue margins and bold text in the Inspector.
