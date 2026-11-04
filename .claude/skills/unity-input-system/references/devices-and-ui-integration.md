# Devices and UI Integration

Docs (1.20 manual): `devices-overview`, `read-devices-directly`, `ui-input`, `introduction-ui-input-module`, `configure-ui-input-action-map`. Canvas layout beyond the module: `ui-engineer` (`ugui`, `ui-toolkit`).

## Device categories
| Category | Note |
|---|---|
| Pointer | Mouse, pen, touchscreen share one base: pointer-position code written against it works on all three |
| Keyboard | Key input and the text-input channel are different things |
| Gamepad / Joystick | Gamepad is the fixed two-stick layout; a flight stick is a Joystick |
| Sensors | Must be enabled explicitly; affected by orientation compensation |
| HID | Generic fallback and route to a custom layout |
| Tracked | Raw XR pose/button input: this skill stops here |

## Direct reads
- Current-device properties return the last-used device or null: null-check every read.
- Forfeits rebinding, composites, Processors (deadzones) and scheme matching; the Manual does not recommend it.
- Use was-pressed/was-released queries, not a hand-diffed held state.

## UI
- `InputSystemUIInputModule` replaces the standalone module and feeds uGUI and UI Toolkit.
- A module in the scene takes precedence over the project-wide asset's UI map: check both.
- Navigate/submit/cancel/point/click are ordinary actions; gamepad menu navigation exists only if bound.
- Virtual mouse drives a UI cursor from a stick when no pointer exists.
- A UI click does not suppress a gameplay action on the same control; suppression is an explicit decision.

## On-screen controls
- On-screen button/stick feed a virtual device created from each component's control path.
- Components targeting different device layouts on one screen create several virtual devices and split input the actions expect together.
- Stick behaviour mode (recentre, exact, origin at first touch) decides whether a thumb sliding off the pad keeps steering.

XR rendering and the XR Interaction Toolkit have no owning skill: flag the gap, do not answer from general Input System knowledge.
