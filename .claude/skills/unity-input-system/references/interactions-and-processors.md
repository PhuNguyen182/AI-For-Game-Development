# Interactions and Processors — gesture recognition and value transforms

Sources: [Interactions](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/Interactions.html), [Built-in Interactions](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/built-in-interactions.html), [Processors](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/Processors.html), [Built-in processors](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/built-in-processors.html), [Input settings](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/input-settings.html).
Covers: SKILL.md §4 — **"Add an Interaction only when a timing pattern is genuinely required"**.

Two things attach to a binding and are easy to confuse: a Processor rewrites
the value, an Interaction decides when the action reaches its phases. The
second is the one that can stop an action firing at all, so it is the first
thing to check when a correctly bound action does nothing.

## Interactions

| Interaction | Performs when | Cancels when | Source |
|---|---|---|---|
| Press | The actuation crosses the press point, or falls back below it, or both, depending on its behaviour setting | Not applicable in the press-only form | [Built-in Interactions](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/built-in-interactions.html) |
| Hold | The control has stayed above the press point for the full duration — while still held, not on release | Released before the duration elapses | [Built-in Interactions](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/built-in-interactions.html) |
| Tap | Released within the duration | Held past the duration, so a slow tap becomes nothing at all rather than a hold | [Built-in Interactions](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/built-in-interactions.html) |
| Slow Tap | Released after the minimum duration — the exact inverse of Tap, and the pair are routinely swapped by mistake | Released too early | [Built-in Interactions](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/built-in-interactions.html) |
| Multi Tap | The full sequence of taps completes within its count, spacing and per-tap duration | A tap is held too long, or the gap between taps exceeds the allowed delay | [Built-in Interactions](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/built-in-interactions.html) |

**Critical caveat**: an Interaction whose gesture the player never performs
means the action never performs either. A Hold on a button players tap reads
as a dead binding, and nothing in the Inspector or the console says so.

## Processors

| Processor | Operand | Effect | Source |
|---|---|---|---|
| Clamp | float | Restricts to a minimum and maximum | [Built-in processors](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/built-in-processors.html) |
| Invert, Invert Vector 2 and 3 | float, vectors | Negates, per axis for the vector forms — the correct place for an inverted-look option rather than a sign flip in gameplay code | [Built-in processors](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/built-in-processors.html) |
| Normalize | float | Maps a range onto zero-to-one, or onto minus-one-to-one when the minimum sits below the zero point | [Built-in processors](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/built-in-processors.html) |
| Normalize Vector 2 and 3 | vectors | Reduces to unit length | [Built-in processors](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/built-in-processors.html) |
| Scale, Scale Vector 2 and 3 | float, vectors | Multiplies, per axis for the vector forms — sensitivity belongs here | [Built-in processors](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/built-in-processors.html) |
| Axis Deadzone | float | Snaps below the minimum to zero and clamps above the maximum — the trigger and single-axis case | [Built-in processors](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/built-in-processors.html) |
| Stick Deadzone | `Vector2` | Applies the deadzone to the vector's magnitude rather than per axis, so diagonal input is not penalised the way a per-axis deadzone penalises it | [Built-in processors](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/built-in-processors.html) |

| Subject | What it decides | Source |
|---|---|---|
| Project-wide default deadzones | Applied automatically unless a binding overrides them, so a per-binding deadzone added without checking either duplicates the default or fights it | [Input settings](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/input-settings.html) |
| Custom Interaction or Processor | An extension point registered before any asset references it by name; most requests that sound custom are a built-in variant plus timing logic that belongs in Shared Core | [Interactions](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/Interactions.html) |
