# Devices and UI Integration — direct reads, the UI module, on-screen controls, XR boundary

Sources: [Types of input devices](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/devices-overview.html), [Read devices directly](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/read-devices-directly.html), [Input for user interfaces](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/ui-input.html), [Introduction to the UI Input Module](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/introduction-ui-input-module.html), [Configure UI Input Actions](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/configure-ui-input-action-map.html), [InputDevice API](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/api/UnityEngine.InputSystem.InputDevice.html).
Covers: SKILL.md §4 — **"Drive UI through `InputSystemUIInputModule` on the scene's `EventSystem`"**.

How input reaches a device read, a UI callback, or a touchscreen overlay. The
Canvas hierarchy and widget design on the other side of the module belong to
`ui-ux-programmer`; the XR surface named at the end has no owner here.

## Device categories

| Category | What it decides | Source |
|---|---|---|
| Pointer devices | Mouse, pen and touchscreen share one base, so pointer-position code written against that base works across all three without branching | [Types of input devices](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/devices-overview.html) |
| Keyboard | Key input plus a separate text-input channel, which is not the same thing as a key binding | [Types of input devices](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/devices-overview.html) |
| Gamepad and Joystick | Gamepad is the fixed two-stick layout; Joystick is the looser device with at least one stick and buttons, so a flight stick is not a gamepad | [Types of input devices](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/devices-overview.html) |
| Sensors | Accelerometer, gyroscope and the rest; they must be enabled explicitly and are affected by the orientation-compensation setting | [Types of input devices](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/devices-overview.html) |
| HID | The generic fallback for hardware with no dedicated class, and the route to a custom layout | [Types of input devices](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/devices-overview.html) |
| Tracked devices | Raw pose and button input from XR hardware — the boundary of this skill, and no further | [Types of input devices](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/devices-overview.html) |

## Direct reads

| Subject | What it decides | Source |
|---|---|---|
| The current-device properties | Return the most recently used device of that type, or nothing when none is connected, so every read needs a null check | [Read devices directly](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/read-devices-directly.html) |
| What direct reading forfeits | Rebinding, composites, Processors including deadzones, and control-scheme matching — the Manual states plainly that this is not the recommended workflow | [Read devices directly](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/read-devices-directly.html) |
| Frame-scoped queries | The was-pressed and was-released queries account for event processing order; diffing a held state by hand does not, and misses same-frame pairs | [Read devices directly](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/read-devices-directly.html) |

## UI integration

| Subject | What it decides | Source |
|---|---|---|
| `InputSystemUIInputModule` | Replaces the legacy standalone module on the scene's event system and feeds both uGUI and UI Toolkit | [Introduction to the UI Input Module](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/introduction-ui-input-module.html) |
| Precedence | A module present in the scene takes priority over the UI map configured on the project-wide asset, so checking only one of the two explains nothing | [Configure UI Input Actions](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/configure-ui-input-action-map.html) |
| UI action map | Navigate, submit, cancel, point and click are actions like any other, and gamepad menu navigation exists only because they are bound | [Configure UI Input Actions](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/configure-ui-input-action-map.html) |
| Virtual mouse | Drives a UI cursor from a stick where no pointer device exists, which is what makes a controller-only build usable on a pointer-designed UI | [Input for user interfaces](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/ui-input.html) |
| No input consumption | A UI click does not suppress a gameplay action bound to the same control; both fire, and suppression is an explicit decision | [Input for user interfaces](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/ui-input.html) |

## On-screen controls

| Subject | What it decides | Source |
|---|---|---|
| On-screen button and stick | Feed a virtual device created from the control path each component targets, so a touch control is indistinguishable from real hardware downstream | [Input for user interfaces](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/ui-input.html) |
| Mixed control paths | Components on one screen targeting different device layouts create several virtual devices at once, which splits the input the actions expect to see together | [Input for user interfaces](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/ui-input.html) |
| Stick behaviour mode | Whether the stick recentres, tracks exactly, or moves its origin to the first touch — the setting that decides whether a thumb sliding off the pad keeps steering | [Input for user interfaces](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/ui-input.html) |

**Critical caveat**: raw tracked-device pose input is where this skill stops.
XR rendering configuration and the XR Interaction Toolkit package are a much
larger surface with no owning skill in this project — flag that gap rather
than answering from general Input System knowledge.
