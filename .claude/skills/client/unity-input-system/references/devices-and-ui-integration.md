# Devices, Direct Polling & UI Integration

[Manual — Types of input devices](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/devices-overview.html) · [Read devices directly](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/read-devices-directly.html) · [Manual — Input for user interfaces](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/ui-input.html) · [Introduction to the UI Input Module](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/introduction-ui-input-module.html) · [Configure UI Input Actions](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/configure-ui-input-action-map.html) · [API — InputDevice](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/api/UnityEngine.InputSystem.InputDevice.html) · [API — InputControl\<TValue\>](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/api/UnityEngine.InputSystem.InputControl-1.html)

## Device categories

[devices-overview.html](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/devices-overview.html):

- **Pointers** — devices that track a 2D screen position: `Mouse`, `Touchscreen`, `Pen` all derive from the common `Pointer` base.
- **Keyboard** — `Keyboard`, key-based input, including raw text input capture (see the Keyboard-specific manual chapter for `onTextInput`).
- **Joystick** — "at least one input stick and button," a more generic device than `Gamepad`.
- **Gamepad** — the Xbox-style layout: two thumbsticks, D-pad, four face buttons, two shoulder buttons, two triggers. Sub-pages cover PlayStation/Switch/Xbox-specific gamepad layouts and haptics.
- **Sensors** — accelerometer, gyroscope, gravity, attitude, light, humidity, pressure, proximity, step counter, and more — devices "measur[ing] environmental characteristics."
- **HID (Human Interface Device)** — the generic USB/Bluetooth device specification; used to build a custom layout for a device with no dedicated Unity class.
- **Tracked/XR devices** — `TrackedDevice` and XR-specific pose input; see [on-screen-controls-and-xr.md](on-screen-controls-and-xr.md) for the boundary this skill draws around XR.

## `InputDevice` / `InputControl` — reading raw state

`InputDevice` (`deviceId`, `description`, `allControls` — a flattened, non-allocating read of every control on the device, `added`, `enabled`, `native`) is the root of a control hierarchy; `InputControl<TValue>` (`device`, `parent`, `name`, `path`, `children`, `ReadValue()`, `ReadUnprocessedValue()`) is the typed leaf/branch node. Concrete controls (`ButtonControl`, `AxisControl`, `Vector2Control`, …) derive from `InputControl<TValue>`. Full member tables: [scripting-api.md](scripting-api.md).

## Direct device polling — `Gamepad.current`, `Keyboard.current`, `Mouse.current`

[read-devices-directly.html](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/read-devices-directly.html):

```csharp
Gamepad gamepad = Gamepad.current;
if (gamepad != null && gamepad.buttonSouth.wasPressedThisFrame)
{
    // ...
}
```

The `.current` static property returns the most recently active device of that type (or `null` if none is connected — **always null-check**). This is the "Direct" workflow from [Workflows.html](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/Workflows.html), explicitly **not the recommended default**: "This isn't generally the recommended workflow because it bypasses many of the Input System's useful features, such as actions and bindings." Concretely, direct polling loses rebinding support, composite bindings, deadzone/processor pipelines, and control-scheme device matching. Reserve it for fast prototyping or a genuinely fixed, single-platform input scheme — not for production multi-platform/rebindable input, which should go through Actions instead (see [actions-bindings-and-assets.md](actions-bindings-and-assets.md)).

## UI integration — `InputSystemUIInputModule`

[introduction-ui-input-module.html](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/introduction-ui-input-module.html): `InputSystemUIInputModule` is the Input-System-driven replacement for the legacy `StandaloneInputModule`, sitting on the scene's `EventSystem` GameObject and feeding both uGUI and UI Toolkit through the same `BaseInputModule` infrastructure. **Required** for uGUI/UI Toolkit input in Unity versions prior to 2023.2. A component-level `InputSystemUIInputModule` in the scene **takes priority over** the UI action-map settings baked into the project-wide actions asset — don't assume the project-wide asset's UI map is what's actually driving the UI once a scene-level module is present; check both.

This skill's boundary here is deliberately narrow: it covers wiring the `InputSystemUIInputModule` itself (assigning its action references, `EventSystem` setup, per-camera restriction for split-screen via `MultiplayerEventSystem`) — it does **not** cover the actual screen layout, Canvas hierarchy, or visual widget design those input events eventually reach. That's `ui-ux-programmer`'s territory once input arrives at a UI event callback.

**Known UI-integration limitations** (see [migration-and-settings.md](migration-and-settings.md) for the full Known Limitations list): the Input System cannot feed IMGUI (`OnGUI`) at all; UI Toolkit currently supports only pointer (mouse/pen/touch) and gamepad input, not full keyboard navigation; text input cannot be routed into uGUI/TextMesh Pro fields through the new system — those still need the legacy path for text entry.

## Virtual Mouse (for UI cursor control without a real mouse)

A `VirtualMouseInput` component lets a gamepad/keyboard drive a synthetic on-screen cursor for UI navigation on platforms with no physical pointer (consoles, some mobile setups) — see the Manual's "Use a Virtual Mouse for UI cursor control" chapter, reachable from [devices-overview.html](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/devices-overview.html)'s sibling nav. In scope for this skill as device/UI-module plumbing; the cursor's *visual* representation (the sprite/graphic it drags around) is `ui-ux-programmer`'s territory, same boundary as the rest of UI integration above.
