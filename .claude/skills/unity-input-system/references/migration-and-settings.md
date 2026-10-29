# Migration and Settings

Docs (1.20 manual): `enable-correct-input-system`, `migrate-from-old-input-system`, `input-settings`, `KnownLimitations`, `update-mode`, `timing-and-latency`.

## Active Input Handling
`Edit → Project Settings → Player → Other Settings → Active Input Handling`.

| Setting | Effect |
|---|---|
| Input Manager (Old) | Only legacy runs; every API here is inert |
| Input System Package (New) | Only this package runs; `UnityEngine.Input` receives nothing |
| Both | Both run (`ENABLE_INPUT_SYSTEM` / `ENABLE_LEGACY_INPUT_MANAGER`); migration mode with real overhead, not a default to leave |

Migrate a feature's input model, not call sites: a one-to-one swap of legacy calls is what the Manual calls the least flexible option and discards rebinding, composites and scheme matching.

## InputSettings
| Setting | Decides |
|---|---|
| Update Mode | When events process (table below) |
| Background behaviour | Whether devices produce input while unfocused; tied to run-in-background |
| Default deadzones | Project-wide fallback for every stick/axis Processor; check before adding a per-binding deadzone |
| Compensate orientation | Adjusts sensors for screen orientation; silently changes accelerometer axes |
| Supported devices | Trims unused device layouts from the player |

## Update Modes
| Mode | Choose when |
|---|---|
| Process events in dynamic update | Logic reads in `Update` (common) |
| Process events in fixed update | Physics-driven movement; input and physics share a clock |
| Process events manually | Deterministic replay, recording, or a test harness owning the clock |

Reading one action from both `Update` and `FixedUpdate` in a frame sees different lifecycle points. Use the frame-scoped pressed/released queries; hand-diffing a held state misses or double-counts a same-frame press and release.

Actions are a rebindable view over device state: to synthesise input, queue an event, never write an action's value.

## Documented gaps
Versioned list: re-read `KnownLimitations` for the installed version before committing a design to an entry.

| Gap | Consequence |
|---|---|
| No IMGUI support | Immediate-mode UI cannot be driven |
| No text entry into uGUI / TextMesh Pro | Typing still needs the legacy path |
| UI does not consume input | UI click and a gameplay action on the same control both fire; suppression is an explicit check |
| Split-screen `PlayerInput` + Cinemachine | Documented incompatible: surface at design time, route the camera half to `unity-cinemachine-authoring` |
| No state resync after focus loss | A key held across focus loss is not seen as held on return |
| One touchscreen device on Android | Multiple touch surfaces not separable |
| No multiple pointers/keyboards on desktop | Two mice or keyboards are not distinct devices |
| No HID in 32-bit players | HID controllers absent on 32-bit targets |
| Unity Remote unsupported | Use the Device Simulator |
