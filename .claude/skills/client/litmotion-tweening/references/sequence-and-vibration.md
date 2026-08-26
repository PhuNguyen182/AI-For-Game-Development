# Sequence & Punch/Shake — Composing and Vibrating Motions

Sources: [Sequence](https://annulusgames.github.io/LitMotion/articles/en/sequence.html), [Vibration Motion with Punch/Shake](https://annulusgames.github.io/LitMotion/articles/en/punch-and-shake.html), verified against [`LSequence.cs`](https://github.com/annulusgames/LitMotion/blob/main/src/LitMotion/Assets/LitMotion/Runtime/LSequence.cs), [`MotionSequenceBuilder.cs`](https://github.com/annulusgames/LitMotion/blob/main/src/LitMotion/Assets/LitMotion/Runtime/MotionSequenceBuilder.cs), [`LMotion.Punch.cs`](https://github.com/annulusgames/LitMotion/blob/main/src/LitMotion/Assets/LitMotion/Runtime/LMotion.Punch.cs), [`LMotion.Shake.cs`](https://github.com/annulusgames/LitMotion/blob/main/src/LitMotion/Assets/LitMotion/Runtime/LMotion.Shake.cs).
Covers: SKILL.md §4 — **"Reach for `LSequence` only for structural composition"**.

`LSequence.Create()` returns a `MotionSequenceBuilder` struct; `Run()` starts
it and returns a `MotionHandle` for the whole sequence, controllable exactly
like any other motion (see [motion-builder-and-handle.md](motion-builder-and-handle.md)).

## `LSequence` methods

| Method | Effect | Source |
|---|---|---|
| `Append(MotionHandle)` | Plays after the previously appended motion finishes | [`MotionSequenceBuilder.cs`](https://github.com/annulusgames/LitMotion/blob/main/src/LitMotion/Assets/LitMotion/Runtime/MotionSequenceBuilder.cs) |
| `AppendInterval(float)` | Inserts a pause of `interval` seconds after the last appended motion | same |
| `Join(MotionHandle)` | Starts at the same time as the previously added motion (parallel) | same |
| `Insert(float position, MotionHandle)` | Starts the motion at an explicit time offset from the sequence start | same |
| `Run()` | Starts the sequence; returns the sequence's own `MotionHandle` | same |
| `Run(Action<MotionBuilder<double,NoOptions,DoubleMotionAdapter>> configuration)` | Same, but lets the caller configure the sequence's own driving motion (e.g. `WithLoops`, `WithScheduler`, `WithOnComplete` for the whole sequence) | same |

```csharp
LSequence.Create()
    .Append(LMotion.Create(0f, 1f, 1f).BindToPositionX(transform))
    .AppendInterval(0.5f)
    .Join(LMotion.Create(0f, 1f, 1f).BindToPositionY(transform))
    .Insert(0.2f, LMotion.Create(0f, 1f, 1f).BindToPositionZ(transform))
    .Run();
```

**Critical caveat**: a motion that is already playing, or one built with `WithLoops(-1)` (infinite), cannot be added to a sequence — `Append`/`Join`/`Insert` throw. Create each motion fresh for the sequence and give it a finite loop count.

**Critical caveat**: `LSequence` intentionally has no `AppendCallback()` — a callback belongs at a motion's own `WithOnComplete()`, or the whole thing should be procedural `async`/`await` instead, per SKILL.md §4's guidance on this and [migration-and-rx-integration.md](migration-and-rx-integration.md)'s FAQ notes on the same design reasoning as the missing `DelayedCall()`.

## Punch and Shake

`LMotion.Punch.Create(startValue, strength, duration)` and
`LMotion.Shake.Create(startValue, strength, duration)` animate a value that
oscillates within `startValue ± strength`, rather than progressing linearly
from `from` to `to`.

| Factory | Value types | Behavior | Source |
|---|---|---|---|
| `LMotion.Punch.Create` | `float`, `Vector2`, `Vector3` | Regular, decaying oscillation | [`LMotion.Punch.cs`](https://github.com/annulusgames/LitMotion/blob/main/src/LitMotion/Assets/LitMotion/Runtime/LMotion.Punch.cs) |
| `LMotion.Shake.Create` | `float`, `Vector2`, `Vector3` | Random, decaying oscillation | [`LMotion.Shake.cs`](https://github.com/annulusgames/LitMotion/blob/main/src/LitMotion/Assets/LitMotion/Runtime/LMotion.Shake.cs) |

```csharp
LMotion.Punch.Create(0f, 5f, 2f)
    .WithFrequency(20)
    .WithDampingRatio(0f) // 0 = never settles; 1 (default) = fully damps
    .BindToPositionX(target1);

LMotion.Shake.Create(0f, 5f, 2f)
    .WithFrequency(20)
    .WithRandomSeed(123) // deterministic randomness
    .BindToPositionX(target2);
```

`WithFrequency`/`WithDampingRatio`/`WithRandomSeed` are documented fully in
[motion-settings.md](motion-settings.md)'s Type-restricted `With-` methods table.
