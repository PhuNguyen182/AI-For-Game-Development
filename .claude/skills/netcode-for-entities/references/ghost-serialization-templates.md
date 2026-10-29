# Ghost Serialization Templates

Page (6.6): `ghost-types-templates`. Use only when no native `[GhostField]` support and no `GhostFieldSubType` fits.

## Template file
- Extension `.NetCodeSourceGenerator.additionalfile`; first line `#templateid: Namespace.TemplateName`.
- Regions: `__GHOST_IMPORTS__`, `__GHOST_FIELD__`, `__GHOST_WRITE__`, `__GHOST_READ__`, `__GHOST_COPY_TO_SNAPSHOT__`, `__GHOST_PREDICT__`, `__GHOST_CALCULATE_CHANGE_MASK__`, `__GHOST_REPORT_PREDICTION_ERROR__`.
- `__GHOST_COPY_FROM_SNAPSHOT__` is required for `Clamp`; `__GHOST_COPY_FROM_SNAPSHOT_INTERPOLATE__` (+ `_SETUP__`, `_DISTSQ__`, `_CLAMP_MAX__`) for `Interpolate`/`InterpolateAndExtrapolate`.
- Tokens: `__GHOST_FIELD_NAME__`, `__GHOST_FIELD_REFERENCE__`, `__GHOST_MASK_INDEX__`, `__GHOST_QUANTIZE_SCALE__`, `__GHOST_DEQUANTIZE_SCALE__`.

## Registration
Add a `TypeRegistryEntry` in `Unity.NetCode.Generators.UserDefinedTemplates.RegisterTemplates(List<TypeRegistryEntry>, string defaultRootPath)` (partial class, in an assembly the Unity.NetCode generator processes; needs an asmdef reference).

| Field | Meaning |
|---|---|
| `Type` | Full type name |
| `Quantized` | Quantized templates must fill `__GHOST_QUANTIZE_SCALE__` |
| `Smoothing` | Fixes the required regions |
| `SupportCommand` | Type may appear in `ICommandData`/RPCs |
| `Composite` | Container type (`float2`/`float3`); one template for the whole field |
| `Template` | Required `#templateid` |
| `TemplateOverride` | Optional base `#templateid` to reuse sections |

Sub-type: add `public const int MySubType = 1;` to `Unity.NetCode.GhostFieldSubType` (partial), bind via `TypeRegistryEntry.SubType`, then `[GhostField(SubType = GhostFieldSubType.MySubType)]`.

## Limits
- Serialize/Deserialize regions may use only `Packed` and `RawBits` methods (`WriteRawBits(value, bits)`), not unpacked `DataStreamWriter`/`Reader` calls.
- Fixed-list capacity: 1024 in `IRpcCommand`, 64 in component/buffer/command/input.
- Explicit-layout unions: only `Quantized = 0` with `Smoothing = Clamp`.

## Regenerating
Assets → Multiplayer → Force Code Generation. Output is `Temp/NetCodeGenerated`, wiped on close: never commit or hand-edit it.
