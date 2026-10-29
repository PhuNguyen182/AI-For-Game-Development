# Sequence and Punch/Shake

Sources (under the Docs base): sequence, punch-and-shake; source `Runtime/MotionSequenceBuilder.cs`, `LMotion.Punch.cs`, `LMotion.Shake.cs`.

## LSequence

`LSequence.Create()` returns a builder; `Run()` returns one `MotionHandle` for the whole sequence.

| Method | Fact |
|---|---|
| `Append(handle)` | Plays after the previous motion |
| `AppendInterval(float)` | Pause after the last motion |
| `Join(handle)` | Starts with the previous motion |
| `Insert(float position, handle)` | Starts at an offset from sequence start |
| `Run(Action<MotionBuilder<double,NoOptions,DoubleMotionAdapter>>)` | Configure the sequence's own driver (loops, scheduler, `WithOnComplete`) |

```csharp
LSequence.Create()
    .Append(LMotion.Create(0f, 1f, 1f).BindToPositionX(transform))
    .AppendInterval(0.5f)
    .Join(LMotion.Create(0f, 1f, 1f).BindToPositionY(transform))
    .Run();
```

**Caveat:** `Append`/`Join`/`Insert` throw for an already-playing motion or one with `WithLoops(-1)`.

**Caveat:** there is no `AppendCallback`; use a motion's own `WithOnComplete` or procedural `async`/`await`.

## Punch and Shake

`LMotion.Punch.Create` (regular decaying oscillation) and `LMotion.Shake.Create` (random decaying oscillation) take `(startValue, strength, duration)` for `float`, `Vector2`, `Vector3` and oscillate within `startValue ± strength`.

```csharp
LMotion.Punch.Create(0f, 5f, 2f).WithFrequency(20).WithDampingRatio(0f).BindToPositionX(t1);
LMotion.Shake.Create(0f, 5f, 2f).WithFrequency(20).WithRandomSeed(123).BindToPositionX(t2);
```

Option defaults: [motion-settings.md](motion-settings.md).
