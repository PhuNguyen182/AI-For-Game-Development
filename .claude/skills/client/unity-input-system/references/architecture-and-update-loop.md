# Architecture and Update Loop — the pipeline, Update Modes, timing

Sources: [Architecture](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/Architecture.html), [Concepts](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/understanding-input.html), [Workflows](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/Workflows.html), [Update Mode](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/update-mode.html), [Timing and latency](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/timing-and-latency.html).
Covers: SKILL.md §4 — **"Set the Update Mode from where the input-driven logic actually runs"**, **"Choose the consumption workflow from what the feature needs"**.

Where an input value comes from, when it is processed, and which of the three
consumption workflows a feature should use. What the values then mean for the
game is `csharp-engineer`'s Shared Core, not this pipeline.

## The pipeline

| Stage | What it decides | Source |
|---|---|---|
| Native backend | Platform code produces raw event buffers; it ships with the Editor rather than the package, which is why a device can be unsupported on one platform and fine on another | [Architecture](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/Architecture.html) |
| State buffers | Each device holds an unmanaged block of its latest known state, so a read is a memory read rather than a poll of the hardware | [Architecture](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/Architecture.html) |
| Layouts and controls | A layout maps raw memory onto named typed controls, which is what makes a stick readable as a vector rather than as bytes | [Architecture](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/Architecture.html) |
| Actions on top of controls | Actions are a rebindable view over device state, never the state itself — synthesising input means queueing an event, not writing an action's value | [Architecture](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/Architecture.html) |

## Vocabulary

| Term | Meaning | Source |
|---|---|---|
| Device | One piece of hardware — keyboard, mouse, gamepad, touchscreen | [Concepts](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/understanding-input.html) |
| Control | One part of a device that produces a value — a button, a stick, a delta | [Concepts](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/understanding-input.html) |
| Action | A named thing the player wants to do, independent of what drives it | [Concepts](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/understanding-input.html) |
| Action map | A group of actions enabled and disabled as one unit | [Concepts](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/understanding-input.html) |
| Binding | The connection from a control to an action; a composite binds no control itself and aggregates parts instead | [Concepts](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/understanding-input.html) |

Keep these distinct in any handoff — conflating a device with a control, or a
binding with an action, is what makes a bug report unactionable.

## Update Modes

| Mode | Behaviour | Choose when | Source |
|---|---|---|---|
| Process events in dynamic update | Events processed on the variable frame, matching `Update` timing | The input-driven logic reads in `Update` — the common case | [Update Mode](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/update-mode.html) |
| Process events in fixed update | Events processed on the fixed step, matching `FixedUpdate` timing | Movement is physics-driven, so input and physics share one clock | [Update Mode](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/update-mode.html) |
| Process events manually | Nothing is processed until a script asks | Deterministic replay, recording, or a test harness that owns the clock | [Update Mode](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/update-mode.html) |

**Critical caveat**: reading the same action from both `Update` and
`FixedUpdate` in one frame sees it at different points in its lifecycle,
depending on this setting. Use the frame-scoped pressed and released queries
rather than diffing a held state across frames yourself — a same-frame press
and release pair is otherwise missed or double-counted.

## Consumption workflows

| Workflow | What it buys | What it costs | Source |
|---|---|---|---|
| Actions with the generated wrapper | Typed access, compile-time renames, rebinding, composites, schemes | A generated file to keep in sync with the asset | [Workflows](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/Workflows.html) |
| Actions plus `PlayerInput` | Device pairing, per-player state, join and leave handling, split-screen | A component whose notification behaviour must be set correctly — see [player-input-and-multiplayer.md](player-input-and-multiplayer.md) | [Workflows](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/Workflows.html) |
| Direct device reads | The shortest path to a value while prototyping | Rebinding, composites, deadzones and scheme matching, all forfeited, plus a null check on every access | [Workflows](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/Workflows.html) |
