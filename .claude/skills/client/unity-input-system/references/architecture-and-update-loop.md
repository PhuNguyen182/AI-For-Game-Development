# Architecture & Update Loop

[Manual — Architecture](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/Architecture.html) · [Manual — Concepts](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/understanding-input.html) · [Manual — Update Mode](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/update-mode.html) · [Manual — Timing and latency](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/timing-and-latency.html)

## The pipeline: native backend → events → state buffers → controls → actions

The package is a two-tier design: a low-level layer that talks to platform-specific native code, and a high-level layer that gives scripts a typed, device-agnostic API.

1. **Native backend** (shipped with the Unity Editor/Player, not the package itself) collects raw device data per platform and reports it to the managed side as **event buffers** — raw memory streams describing device creation, device removal, and state changes. The managed side can send **commands** back to a device (also as memory buffers) for platform-specific operations (e.g. gamepad rumble).
2. **State buffering.** Each `InputDevice` is backed by a raw, unmanaged memory block holding its current control values. When a state event arrives, the system writes the incoming data into that block, so the buffer always reflects the device's latest known state at the time the event was processed.
3. **Control/Device hierarchy.** A **Layout** describes how raw memory maps to named, typed controls for a given device. From a layout, the high-level system creates an `InputControl` object per control (buttons, sticks, axes) as children of an `InputDevice` — this is what lets script code read `gamepad.leftStick.ReadValue<Vector2>()` instead of interpreting raw bytes. See [scripting-api.md](scripting-api.md) for `InputControl`/`InputDevice` member detail.
4. **Actions sit on top of controls, not the other way around.** An `InputAction` binds to one or more Controls via a control path; the Input System watches those bound Controls for state changes and, when one changes, runs the action's Processors (value transforms) and Interactions (input-pattern recognition, e.g. multi-tap) before notifying game code via callback or making the value available to `ReadValue<T>()`. Raw device state is always the source of truth; Actions are a configurable, rebindable view over it — never edit device state to "fake" an action result, always go through `InputSystem.QueueEvent`/`QueueStateEvent` if a synthetic event is genuinely needed.

`InputSystem` (the static class) is the central hub tying all of this together: `InputSystem.devices` (currently connected devices, no-allocation read), `InputSystem.actions` (the project-wide `InputActionAsset`, if one is assigned), `InputSystem.settings` (global configuration), `InputSystem.onEvent`/`onDeviceChange`/`onActionChange` (observation callbacks), and `InputSystem.Update()` (see below). Full member list in [scripting-api.md](scripting-api.md).

## Update Modes — where `InputSystem.Update()` fits

[Manual — Update Mode](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/update-mode.html), configured via `InputSettings.UpdateMode` (Project Settings → Input System Package).

| Mode | Behavior |
|---|---|
| `ProcessEventsInDynamicUpdate` (Dynamic) | Events are processed at irregular intervals tied to the current framerate — matches `MonoBehaviour.Update()` timing. The default, and the right choice for most gameplay that reads input in `Update()`. |
| `ProcessEventsInFixedUpdate` (Fixed) | Events are processed at fixed-length intervals matching `Time.fixedDeltaTime`, the same cadence as `MonoBehaviour.FixedUpdate()`. Choose this when the input-driven logic itself lives in `FixedUpdate` (e.g. physics-based movement) so input and physics stay on the same clock. |
| `ProcessEventsManually` (Manual) | The Input System does **not** process events on its own — a script must call `InputSystem.Update()` explicitly. Reserved for specialized scenarios needing exact control over when input is processed (e.g. custom replay/record systems, deterministic test harnesses). |

Two further update types (`BeforeRender`, `Editor`) exist for render-thread pose updates and Editor-window input respectively — they don't change how gameplay scripts consume input day to day.

**Mixed timing pitfall**: reading the same action in both `Update()` and `FixedUpdate()` in the same frame can see the value at different points in its lifecycle depending on the configured Update Mode — see [Manual — Timing and latency: Mixed timing scenarios](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/timing-and-latency.html). Decide the Update Mode deliberately based on where the input-driven logic actually lives, rather than leaving the project default unquestioned once a feature depends on tight input-to-physics timing.

## Timing & latency guardrails

[Manual — Timing and latency](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/timing-and-latency.html) covers, at a high level: the input events queue, how to pick a processing mode (above), optimizing for Dynamic vs. Fixed update, and — the sharpest gotcha — **avoiding missed or duplicate events** for discrete inputs (button presses/releases). Checking a button's pressed state at the wrong point in the frame relative to when its event was actually processed can silently miss a same-frame press/release pair, or double-count one. Use `WasPressedThisFrame()`/`WasReleasedThisFrame()` (frame-scoped, correctly account for this) rather than manually diffing `IsPressed()` across two frames yourself.

## Concepts — the vocabulary (for precise cross-references elsewhere in this skill)

[Manual — Concepts](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/understanding-input.html):

- **Device** — a physical piece of hardware (keyboard, mouse, gamepad, touchscreen).
- **Control** — "the separate individual parts of an input device which each send input values into Unity" (a gamepad's buttons/sticks/triggers; a mouse's buttons/delta).
- **Action** — "a high-level concept that describe[s] individual things that a user might want to do," named as a verb (`Jump`, `Move`, `Select`) and independent of which specific device/control drives it.
- **Action Map** — a named group of related Actions that can be enabled/disabled as one unit (e.g. a `Player` map vs. a `UI` map, swapped when opening a menu).
- **Binding** — the connection from a Control to an Action. A normal binding references one control path directly; a **Composite binding** doesn't bind to a control itself — it aggregates several **Part bindings** into one synthesized value (see [actions-bindings-and-assets.md](actions-bindings-and-assets.md)).

Keep this vocabulary precise in any handoff note — "binding" and "action" are not interchangeable, and conflating "device" with "control" is a common source of miscommunication when describing what an `IInputProvider` abstraction should actually expose to `Game.Core.*`.
