# Custom Adapters — Extending LitMotion to New Value Types

Source: [Custom Adapter](https://annulusgames.github.io/LitMotion/articles/en/custom-adapter.html), verified against [`IMotionAdapter.cs`](https://github.com/annulusgames/LitMotion/blob/main/src/LitMotion/Assets/LitMotion/Runtime/IMotionAdapter.cs), [`IMotionOptions.cs`](https://github.com/annulusgames/LitMotion/blob/main/src/LitMotion/Assets/LitMotion/Runtime/IMotionOptions.cs).
Covers: SKILL.md §4 — **"Write a custom `IMotionAdapter<TValue,TOptions>` only for a genuinely unsupported value type"**.

Before writing one, confirm the type is actually missing from
[getting-started.md](getting-started.md)'s Supported Types table — LitMotion
already covers every common Unity value type.

## `IMotionAdapter<TValue, TOptions>`

A stateless `readonly struct` implementing one interpolation method. Adapters
must not carry fields — all state flows through the method's `ref`/`in`
parameters, because the same adapter instance is reused across every motion
of that type combination inside Burst-compiled jobs.

```csharp
using Unity.Jobs;
using UnityEngine;
using LitMotion;

// Required so Burst recognizes the generic job instantiation for this type combination
[assembly: RegisterGenericJobType(typeof(MotionUpdateJob<Vector3, NoOptions, Vector3MotionAdapter>))]

public readonly struct Vector3MotionAdapter : IMotionAdapter<Vector3, NoOptions>
{
    public Vector3 Evaluate(ref Vector3 startValue, ref Vector3 endValue, ref NoOptions options, in MotionEvaluationContext context)
    {
        return Vector3.LerpUnclamped(startValue, endValue, context.Progress);
    }
}
```

| Element | Meaning | Source |
|---|---|---|
| `Evaluate(ref TValue start, ref TValue end, ref TOptions options, in MotionEvaluationContext context)` | The interpolation logic itself | [`IMotionAdapter.cs`](https://github.com/annulusgames/LitMotion/blob/main/src/LitMotion/Assets/LitMotion/Runtime/IMotionAdapter.cs) |
| `context.Progress` | Eased 0–1 progress for the current update | [Custom Adapter](https://annulusgames.github.io/LitMotion/articles/en/custom-adapter.html) |
| `[assembly: RegisterGenericJobType(typeof(MotionUpdateJob<TValue,TOptions,TAdapter>))]` | Registers the concrete generic job so Burst compiles it for this type combination | same |
| `NoOptions` | Use when the motion needs no extra per-instance state | [`IMotionOptions.cs`](https://github.com/annulusgames/LitMotion/blob/main/src/LitMotion/Assets/LitMotion/Runtime/IMotionOptions.cs) |

## `IMotionOptions` — adding extra state

Implement an `unmanaged struct` when the motion needs state beyond start/end/duration (mirroring the built-in `IntegerOptions`):

```csharp
public struct IntegerOptions : IMotionOptions, IEquatable<IntegerOptions>
{
    public RoundingMode RoundingMode;
    // Equals / GetHashCode required by IEquatable<T>
}
```

## Creating motions with the custom adapter

```csharp
LMotion.Create<Vector3, NoOptions, Vector3MotionAdapter>(from, to, duration)
    .BindToPosition(transform);
```

**Critical caveat**: forgetting the `RegisterGenericJobType` assembly attribute is not caught at compile time — LitMotion uses generic Jobs internally, and Burst/IL2CPP need this attribute to know which concrete generic job to ahead-of-time-compile for the new type combination. Always add it in the same change as the adapter, and verify the motion still runs correctly on an IL2CPP device build (per `performance-and-algorithms.md`'s Verification section), not only in the Editor.
