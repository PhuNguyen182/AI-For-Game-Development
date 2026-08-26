# Ghost Authoring — GhostAuthoringComponent, GhostField, GhostComponent, variants

Sources: [Ghosts and snapshots](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/ghost-snapshots.html), [Serialization and synchronization with GhostFieldAttribute](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/ghostfield-synchronize.html), [Customizing replication with GhostComponentAttribute](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/ghostcomponentattribute.html), [Creating replication schemas with GhostComponentVariationAttribute](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/ghost-variants.html), [Apply Variant Overrides from a Baker](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/baker-variant-overrides.html).
Covers: SKILL.md §4 — **"Model every piece of networked state as a ghost, never as a stream of ad hoc RPCs"**.

Declaring a ghost prefab and marking exactly which fields replicate.
Creating/pre-placing ghost instances is [ghost-spawning-and-groups.md](ghost-spawning-and-groups.md);
a type with no native serializer needs [ghost-serialization-templates.md](ghost-serialization-templates.md).

## `GhostAuthoringComponent` — required prefab settings

| Setting | Values | Source |
|---|---|---|
| `SupportedGhostMode` | `All` (both) / `Interpolated` only / `Predicted` only — fixes the ceiling; `DefaultGhostMode` cannot exceed it | [Ghosts and snapshots](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/ghost-snapshots.html) |
| `DefaultGhostMode` | `Interpolated` / `Predicted` / `Owner Predicted` (predicted for the owner, interpolated for everyone else) | [Ghosts and snapshots](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/ghost-snapshots.html) |
| `OptimizationMode` (`GhostOptimizationMode`) | `Dynamic` (default; small snapshot whether changing or not) / `Static` (nothing sent while unchanged, forces single-baseline, incompatible with ghost groups) | [Ghosts and snapshots](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/ghost-snapshots.html) |
| `Importance` | Relative send priority — see [optimization-and-bandwidth.md](optimization-and-bandwidth.md) | [Optimize ghosts](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/optimization/optimize-ghosts.html) |
| `MaxSendRate` | Optional max replication Hz for this prefab's chunks — not strictly enforceable in all cases | [Ghosts and snapshots](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/ghost-snapshots.html) |

For a player-controlled character, `Owner Predicted` is almost always the
right `DefaultGhostMode`: the owner predicts their own input immediately,
every other client interpolates it — see
[time-and-interpolation.md](time-and-interpolation.md) for the tick math
behind that split.

## `[GhostField]`

Struct must be a concrete `public`/`internal` `IComponentData` (or
`IBufferElementData`, with **every** public field annotated — no
`Smoothing`/`MaxSmoothingDistance` support on buffers). Only `public`
members serialize.

| Parameter | Default | Effect | Source |
|---|---|---|---|
| `Quantization` | Disabled | Multiplies a float by this factor and sends as an integer — the main bandwidth lever | [GhostFieldAttribute](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/ghostfield-synchronize.html) |
| `Composite` | Disabled | One change-bit for the whole struct instead of one per field | [GhostFieldAttribute](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/ghostfield-synchronize.html) |
| `SendData` | Enabled | `false` excludes the field from serialization entirely | [GhostFieldAttribute](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/ghostfield-synchronize.html) |
| `Smoothing` | `Clamp` | `Clamp` / `Interpolate` / `InterpolateAndExtrapolate` — client-side handling in interpolated mode | [GhostFieldAttribute](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/ghostfield-synchronize.html) |
| `MaxSmoothingDistance` | none | Disables interpolation once the change between snapshots exceeds this | [GhostFieldAttribute](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/ghostfield-synchronize.html) |
| `SubType` | default | Selects a custom serializer, per [ghost-serialization-templates.md](ghost-serialization-templates.md) | [GhostFieldAttribute](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/ghostfield-synchronize.html) |

```csharp
public struct MySerializedComponent : IComponentData
{
    [GhostField] public int MyIntField;
    [GhostField(Quantization = 1000)] public float MyFloatField;
    [GhostField(Quantization = 1000, Smoothing = SmoothingAction.Interpolate)]
    public float2 Position;
    public float2 NonSerializedField; // no [GhostField] -> never sent
}
```

`[GhostField]` on a non-primitive field is inherited by its subfields
(except `SubType`, which resets to default). Static-optimized ghosts never
extrapolate, regardless of `Smoothing`.

## `[GhostComponent]` — replication of the whole component

| Property | Options | Default | Source |
|---|---|---|---|
| `PrefabType` (`GhostPrefabType`) | `None` / `All` / `Server` / `Client` / `AllPredicted` / `PredictedClient` / `InterpolatedClient` | `All` | [GhostComponentAttribute](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/ghostcomponentattribute.html) |
| `OwnerSendType` (`SendToOwnerType`) | `None` / `All` / `SendToOwner` / `SendToNonOwner` | `All` | [GhostComponentAttribute](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/ghostcomponentattribute.html) |
| `SendTypeOptimization` (`GhostSendType`) | `AllClients` / `OnlyPredictedClients` / `OnlyInterpolatedClients` / `DontSend` | `AllClients` | [GhostComponentAttribute](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/ghostcomponentattribute.html) |
| `SendDataForChildEntity` | `bool` | `false` | [GhostComponentAttribute](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/ghostcomponentattribute.html) |

Example: `[GhostComponent(PrefabType=GhostPrefabType.Client)]` on a
`RenderMesh`-carrying component keeps rendering data off the server's copy
of the prefab entirely. `[GhostComponent]` only takes effect on a component
that already carries at least one `[GhostField]`.

## Variants — replicating a type you cannot edit

`[GhostComponentVariation(typeof(Target), "Variant Name")]` on a proxy
struct, combined with `[GhostComponent]`/`[GhostField]` on that proxy,
declares a replication schema for `Target` without modifying it — needed
for third-party or built-in types (e.g. `LocalTransform`).

```csharp
[GhostComponentVariation(typeof(LocalTransform), "Transform - 2D")]
[GhostComponent(PrefabType = GhostPrefabType.All)]
public struct PositionRotation2d
{
    [GhostField(Quantization = 1000, Smoothing = SmoothingAction.InterpolateAndExtrapolate,
        SubType = GhostFieldSubType.Translation2D)]
    public float3 Position;
    [GhostField(Quantization = 1000, Smoothing = SmoothingAction.InterpolateAndExtrapolate,
        SubType = GhostFieldSubType.Rotation2D)]
    public quaternion Rotation;
}
```

| Built-in variant | Effect | Source |
|---|---|---|
| `ClientOnlyVariant` | Component exists only on client Worlds | [Ghost variants](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/ghost-variants.html) |
| `ServerOnlyVariant` | Component exists only on server Worlds | [Ghost variants](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/ghost-variants.html) |
| `DontSerializeVariant` | Disables serialization entirely | [Ghost variants](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/ghost-variants.html) |

Register a project-wide default via a `DefaultVariantSystemBase` subclass
overriding `RegisterDefaultVariants`; override per-prefab with
`GhostAuthoringInspectionComponent` in the Editor, or from a `Baker` via a
`GhostVariantBakedOverride` buffer and `GhostVariantOverrideBakerExtensions`
(`AppendDontSerializeOverride`, `AppendPrefabTypeOverride`,
`AppendSendTypeOverride`, `AppendOverride<TVariant>`) — a baking-only
buffer that never reaches the runtime World. An
`GhostAuthoringInspectionComponent` entry on the prefab wins over a baker
override for the same component.

**Critical caveat**: ghost component variants for `IBufferElementData` are
not fully supported — prefer plain `[GhostField]` on the buffer element type
directly when the buffer's owner is one you can edit.
