# Ghost Serialization Templates — custom types the code generator doesn't know

Sources: [Ghost Type Templates](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/ghost-types-templates.html).
Covers: SKILL.md §4 — **"Model every piece of networked state as a ghost, never as a stream of ad hoc RPCs"**, escalation branch.

Reach for this only when a field's type has no native `[GhostField]` support
and no existing `GhostFieldSubType` fits — most gameplay data serializes
through [ghost-authoring.md](ghost-authoring.md) without ever needing a
custom template. This is source-generator territory: the generator extracts
named regions from a template file and substitutes reserved keywords with
the real field name at compile time.

## Template file

- File extension `.NetCodeSourceGenerator.additionalfile`, first line
  `#templateid: Namespace.TemplateName`.
- Regions: `__GHOST_IMPORTS__`, `__GHOST_FIELD__`, `__GHOST_WRITE__`,
  `__GHOST_READ__`, `__GHOST_COPY_TO_SNAPSHOT__`,
  `__GHOST_COPY_FROM_SNAPSHOT__` (required for `Clamp`),
  `__GHOST_COPY_FROM_SNAPSHOT_INTERPOLATE__` (+ `_SETUP__`/`_DISTSQ__`/
  `_CLAMP_MAX__`, required for `Interpolate`/`InterpolateAndExtrapolate`),
  `__GHOST_PREDICT__`, `__GHOST_CALCULATE_CHANGE_MASK__`,
  `__GHOST_REPORT_PREDICTION_ERROR__`.
- Reserved substitution tokens: `__GHOST_FIELD_NAME__`,
  `__GHOST_FIELD_REFERENCE__`, `__GHOST_MASK_INDEX__`,
  `__GHOST_QUANTIZE_SCALE__`, `__GHOST_DEQUANTIZE_SCALE__`.

## Registering a template

```csharp
namespace Unity.NetCode.Generators
{
    public static partial class UserDefinedTemplates
    {
        static partial void RegisterTemplates(
            System.Collections.Generic.List<TypeRegistryEntry> templates,
            string defaultRootPath)
        {
            templates.AddRange(new[]
            {
                new TypeRegistryEntry
                {
                    Type = "MyCustomNamespace.MyCustomType",
                    Quantized = true,
                    Smoothing = SmoothingAction.InterpolateAndExtrapolate,
                    SupportCommand = false,
                    Composite = false,
                    Template = "MyCustomNamespace.MyCustomTypeTemplate",
                    TemplateOverride = "",
                },
            });
        }
    }
}
```

This partial class must be reachable from an assembly the `Unity.NetCode`
source generator processes (assembly definition reference required).

## `TypeRegistryEntry` fields

| Field | Meaning | Source |
|---|---|---|
| `Type` | Full type name the template applies to | [Ghost Type Templates](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/ghost-types-templates.html) |
| `Quantized` | Whether values are quantized — quantized templates must fill `__GHOST_QUANTIZE_SCALE__` | [Ghost Type Templates](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/ghost-types-templates.html) |
| `Smoothing` | `Clamp` / `Interpolate` / `InterpolateAndExtrapolate` — fixes which regions are required | [Ghost Type Templates](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/ghost-types-templates.html) |
| `SupportCommand` | Whether the type may appear inside `ICommandData`/RPCs | [Ghost Type Templates](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/ghost-types-templates.html) |
| `Composite` | Applies to container types (`float2`/`float3`) — one template covers the whole field | [Ghost Type Templates](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/ghost-types-templates.html) |
| `Template` | Required — the `#templateid` this entry uses | [Ghost Type Templates](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/ghost-types-templates.html) |
| `TemplateOverride` | Optional base template's `#templateid`, for section reuse | [Ghost Type Templates](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/ghost-types-templates.html) |

## `SubType` registration

```csharp
namespace Unity.NetCode
{
    public static partial class GhostFieldSubType
    {
        public const int MySubType = 1;
    }
}
```
Reference it as `[GhostField(SubType = GhostFieldSubType.MySubType)]` once
registered against a `TypeRegistryEntry.SubType` binding.

## Limits and constraints

| Constraint | Value | Source |
|---|---|---|
| Serialize/Deserialize region methods | Only `Packed` and `RawBits` methods (e.g. `WriteRawBits(value, bits)`); unpacked `DataStreamWriter`/`Reader` calls forbidden | [Ghost Type Templates](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/ghost-types-templates.html) |
| Fixed-list capacity, `IRpcCommand` | 1024 | [Ghost Type Templates](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/ghost-types-templates.html) |
| Fixed-list capacity, component/buffer/command/input | 64 | [Ghost Type Templates](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/ghost-types-templates.html) |
| C# unions (explicit layout) | Only `Quantized = 0` + `Smoothing = Clamp` supported | [Ghost Type Templates](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/ghost-types-templates.html) |

Regenerate manually via **Assets → Multiplayer → Force Code Generation**;
output lands in `Temp/NetCodeGenerated`, deleted when Unity closes.

**Critical caveat**: the generated serializers live only in `Temp/`, never
commit them and never hand-edit them — a template change and a forced
regeneration is the only supported way to change generated serialization
code.
