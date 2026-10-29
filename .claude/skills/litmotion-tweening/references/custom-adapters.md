# Custom Adapters

Sources (under the Docs base): custom-adapter; source `Runtime/IMotionAdapter.cs`, `IMotionOptions.cs`.

Check [getting-started.md](getting-started.md) first: every common Unity value type is already supported.

An adapter is a stateless `readonly struct` with one `Evaluate`; it carries no fields because one instance serves every motion of the type combination inside Burst jobs.

```csharp
[assembly: RegisterGenericJobType(typeof(MotionUpdateJob<Vector3, NoOptions, Vector3MotionAdapter>))]

public readonly struct Vector3MotionAdapter : IMotionAdapter<Vector3, NoOptions>
{
    public Vector3 Evaluate(ref Vector3 startValue, ref Vector3 endValue, ref NoOptions options, in MotionEvaluationContext context)
        => Vector3.LerpUnclamped(startValue, endValue, context.Progress);
}

LMotion.Create<Vector3, NoOptions, Vector3MotionAdapter>(from, to, duration).BindToPosition(transform);
```

| Element | Fact |
|---|---|
| `context.Progress` | Eased 0-1 progress |
| `NoOptions` | Use unless the motion needs extra per-instance state |
| Custom options | An `unmanaged` struct implementing `IMotionOptions` and `IEquatable<T>`, like built-in `IntegerOptions` |

**Caveat:** a missing `RegisterGenericJobType` is not a compile error; Burst/IL2CPP cannot precompile the job. Add it with the adapter and verify on an IL2CPP device build, not only in the Editor.
