# Editor Tooling & Debugging

[Manual — Input Actions Editor references](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/actions-editor.html) · [Input Actions Editor window reference](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/input-actions-editor-window-reference.html) · [Manual — Debugging](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/Debugging.html) · [The input debugger window](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/the-input-debugger-window.html) · [Device Simulation](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/device-simulation.html) · [Manual — Testing](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/Testing.html)

## Input Actions Editor window

[input-actions-editor-window-reference.html](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/input-actions-editor-window-reference.html) — the authoring surface for an `.inputactions` asset, three panels:

1. **Action Maps panel** — the list of action maps in the asset, with an Add (+) button to create a new one.
2. **Actions panel** — every action (and its bindings) inside the currently selected action map, with Add (+) for new actions/bindings.
3. **Properties panel** — properties of whatever is currently selected in the Actions panel (an action's type/interactions/processors, or a binding's path/groups) — the panel's title/contents adapt to whether an action or a binding is selected.

Prefer this window as the default authoring path for anything a designer or engineer will tune more than once (per KISS in `coding-principles.md`) — see [actions-bindings-and-assets.md](actions-bindings-and-assets.md) for when scripted/JSON configuration is the better fit instead.

## Input Debugger

[the-input-debugger-window.html](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/the-input-debugger-window.html) — **Window → Analysis → Input Debugger**. Sections:

- **Devices** — every currently connected device, plus any unrecognized hardware Unity couldn't match to a layout.
- **Layouts** — the registered database of Control/Device layouts.
- **Actions** — visible only in Play mode, only once at least one action is enabled; shows enabled actions and their resolved control bindings live.
- **Users** — appears once `InputUser` instances exist (this is what backs `PlayerInput`); shows each user's control scheme, paired devices, and bound actions.
- **Settings & Metrics** — the live `InputSettings` configuration plus resource-usage statistics.

This is the first stop for "why isn't my binding resolving" or "why did the wrong device get paired" — check the live Actions/Users panels in Play mode before hypothesizing from the asset alone, since binding resolution depends on which devices are actually connected/paired at runtime, not just what the asset declares.

## Device Simulator

[device-simulation.html](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/device-simulation.html) — an Editor window that converts mouse/pen input into simulated touchscreen input while it's open, creating its own virtual `Touchscreen` device and **disabling native mouse/pen devices** for the duration. Useful for testing touch-specific interaction code (on-screen controls, multi-touch gestures) without physical touch hardware — remember the native pointer devices are suppressed while the window is focused, which can make an unrelated mouse-driven Editor workflow look "broken" if the simulator window is left open by mistake.

## Testing

[Testing.html](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/Testing.html) covers `InputTestFixture` (base class for Input-System-aware Unity Test Framework tests), setting up a test assembly that references the Input System, and synthesizing input events in a test (`InputTestFixture.Press()`/`.Release()`/`Set()` helpers, or raw `InputSystem.QueueStateEvent`). This is `qa-automation-engineer`'s territory once code has passed Code Review — this skill's role stops at making the input-layer code itself testable (e.g. behind an `IInputProvider` abstraction, per `coding-principles.md`'s Dependency Inversion point), not at writing the test suite.
