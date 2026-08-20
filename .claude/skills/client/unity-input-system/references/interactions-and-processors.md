# Interactions & Processors

[Manual — Interactions](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/Interactions.html) · [Manual — Built-in Interactions](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/built-in-interactions.html) · [Manual — Write custom interactions](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/write-custom-interactions.html) · [Manual — Processors](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/Processors.html) · [Manual — Built-in processors](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/built-in-processors.html) · [Manual — Write custom processors](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/write-custom-processors.html)

Both Interactions and Processors attach to a binding (or the action as a whole); the difference is what they do to the data flowing through it: a **Processor** transforms the *value* (deadzone, invert, scale); an **Interaction** recognizes a *timing pattern* in how a control is actuated (a tap vs. a hold) and drives the action's phase (`Started`/`Performed`/`Canceled`) accordingly. Applying an Interaction with no matching gesture (e.g. `Hold` on an action the player only taps) means the action never reaches `Performed` — a very common source of "my button doesn't seem to work" bug reports.

## Built-in Interactions

[built-in-interactions.html](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/built-in-interactions.html):

| Interaction | Parameters | Phase behavior |
|---|---|---|
| **Press** | `pressPoint`, `behavior` (`PressOnly` / `ReleaseOnly` / `PressAndRelease`) | `PressOnly`: Started+Performed when magnitude crosses `pressPoint`. `ReleaseOnly`: Performed only when magnitude falls back below it. `PressAndRelease`: fires on both the cross and the release. |
| **Hold** | `duration`, `pressPoint` | Started when magnitude exceeds `pressPoint`; Performed only once held above it for the full `duration`; Canceled if released before `duration` elapses. |
| **Tap** | `duration`, `pressPoint` | Started on crossing `pressPoint`; Performed if released **within** `duration`; Canceled if held past `duration` (i.e. a tap held too long becomes a non-event, not a hold — pair with a separate Hold interaction on another binding if both gestures matter). |
| **Slow Tap** | `duration`, `pressPoint` | Started on crossing `pressPoint`; Performed only if released **after** the minimum `duration` (the inverse timing condition of Tap); Canceled if released too early. |
| **Multi Tap** | `tapTime`, `tapDelay`, `tapCount`, `pressPoint` | Started on the first crossing; Performed only once the full tap sequence (count, spacing, per-tap duration) completes; Canceled if a tap is held too long or the gap between taps exceeds `tapDelay`. |

Tap and Slow Tap are direct opposites — mixing them up on the same binding is a common authoring mistake (e.g. wanting "hold to charge" but authoring Tap, which fires on a *quick* release instead).

## Built-in Processors

[built-in-processors.html](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/built-in-processors.html):

| Processor | Operand | Parameters | Effect |
|---|---|---|---|
| **Clamp** | `float` | `min`, `max` | Clamps to `[min..max]`. |
| **Invert** | `float` | — | Multiplies by −1. |
| **Invert Vector 2 / Invert Vector 3** | `Vector2`/`Vector3` | per-axis `invertX/Y/Z` bools | Selectively negates individual axes. |
| **Normalize** | `float` | `min`, `max`, `zero` | Normalizes `[min..max]` to `[0..1]` (unsigned) if `min >= zero`, or `[-1..1]` (signed) if `min < zero`. |
| **Normalize Vector 2 / Vector 3** | `Vector2`/`Vector3` | — | Normalizes to unit length. |
| **Scale** | `float` | `factor` | Multiplies by `factor`. |
| **Scale Vector 2 / Vector 3** | `Vector2`/`Vector3` | per-axis multipliers | Per-axis scale. |
| **Axis Deadzone** | `float` | `min`, `max` | Values below `min` snap to 0; values above `max` clamp to ±1 — the standard trigger/axis deadzone. |
| **Stick Deadzone** | `Vector2` | `min`, `max` | Vectors with magnitude below `min` snap to `(0,0)`; magnitude above `max` normalizes to unit length — the standard analog-stick deadzone, applied to the whole vector's magnitude rather than per-axis (so diagonal input isn't unfairly deadzoned compared to cardinal input). |

**Default project-wide deadzones**: `InputSettings` exposes project-wide default `Axis`/`Stick` deadzone values applied automatically unless a binding overrides them — check the project's `InputSettings` asset before adding a redundant per-binding deadzone processor that duplicates (or conflicts with) the global default.

## Custom Interactions & Processors

Both are extension points: implement `IInputInteraction`/`IInputInteraction<TValue>` for a custom interaction, or subclass `InputProcessor<TValue>` for a custom processor, then register with `InputSystem.RegisterInteraction<T>()` / `InputSystem.RegisterProcessor<T>()` (typically in a `RuntimeInitializeOnLoadMethod`-attributed static method so registration happens before any asset tries to reference it by name). Per KISS/YAGNI in `coding-principles.md`, reach for a custom Interaction/Processor only when a genuine combination of built-ins can't express the requirement — most "custom" input feel requirements (a charged-attack gesture, a directional-swipe recognizer) are actually a Hold/Tap/MultiTap variant plus a bit of Shared-Core-side timing logic, not a reason to write a new `IInputInteraction`.
