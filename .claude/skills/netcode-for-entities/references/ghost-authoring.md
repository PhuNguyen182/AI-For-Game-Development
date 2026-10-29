# Ghost Authoring

Pages (6.6): `ghost-snapshots`, `GhostFieldAttribute`, `GhostComponentAttribute`, ghost variants, variant overrides from a Baker.

## `GhostAuthoringComponent`

| Setting | Values |
|---|---|
| `SupportedGhostMode` | `All` / `Interpolated` / `Predicted`; the ceiling for `DefaultGhostMode` |
| `DefaultGhostMode` | `Interpolated` / `Predicted` / `Owner Predicted` (owner predicts, others interpolate; usual choice for a player character) |
| `OptimizationMode` (`GhostOptimizationMode`) | `Dynamic` (default) / `Static` (nothing sent while unchanged, single baseline, incompatible with ghost groups, never extrapolates) |
| `Importance`, `MaxSendRate` | See [optimization-and-bandwidth.md](optimization-and-bandwidth.md); `MaxSendRate` is not strictly enforceable in all cases |

## `[GhostField]`
- Target: concrete `public`/`internal` `IComponentData`, or `IBufferElementData` with every public field annotated (buffers lack `Smoothing`/`MaxSmoothingDistance`). Only public members serialize. On a non-primitive field, subfields inherit it except `SubType`.

| Parameter | Default | Effect |
|---|---|---|
| `Quantization` | off | float × factor sent as integer; main bandwidth lever |
| `Composite` | off | One change-bit for the whole struct |
| `SendData` | on | `false` excludes the field |
| `Smoothing` | `Clamp` | `Clamp` / `Interpolate` / `InterpolateAndExtrapolate` in interpolated mode |
| `MaxSmoothingDistance` | none | Stops interpolating when the snapshot-to-snapshot change exceeds it |
| `SubType` | default | Custom serializer, see [ghost-serialization-templates.md](ghost-serialization-templates.md) |

```csharp
public struct MyComponent : IComponentData
{
    [GhostField(Quantization = 1000, Smoothing = SmoothingAction.Interpolate)]
    public float2 Position;
    public float2 NotSent; // no attribute, never sent
}
```

## `[GhostComponent]`
Takes effect only on a component with at least one `[GhostField]`.

| Property | Options (default first) |
|---|---|
| `PrefabType` (`GhostPrefabType`) | `All` / `None` / `Server` / `Client` / `AllPredicted` / `PredictedClient` / `InterpolatedClient` |
| `OwnerSendType` (`SendToOwnerType`) | `All` / `None` / `SendToOwner` / `SendToNonOwner` |
| `SendTypeOptimization` (`GhostSendType`) | `AllClients` / `OnlyPredictedClients` / `OnlyInterpolatedClients` / `DontSend` |
| `SendDataForChildEntity` | `false` / `true` |

Example: `PrefabType = Client` on a render component keeps it off the server prefab.

## Variants: replicate a type you cannot edit
`[GhostComponentVariation(typeof(Target), "Name")]` plus `[GhostComponent]`/`[GhostField]` on a proxy struct (e.g. `LocalTransform` as "Transform - 2D" with `SubType = GhostFieldSubType.Translation2D` / `Rotation2D`).
- Built-ins: `ClientOnlyVariant`, `ServerOnlyVariant`, `DontSerializeVariant`.
- Project default: subclass `DefaultVariantSystemBase`, override `RegisterDefaultVariants`.
- Per prefab: `GhostAuthoringInspectionComponent` (wins over a baker override), or a Baker's `GhostVariantBakedOverride` via `GhostVariantOverrideBakerExtensions` (`AppendDontSerializeOverride`, `AppendPrefabTypeOverride`, `AppendSendTypeOverride`, `AppendOverride<TVariant>`); baking-only, never reaches runtime.
- Variants for `IBufferElementData` are not fully supported; annotate an editable buffer element directly.
