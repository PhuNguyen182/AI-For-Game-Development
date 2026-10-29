# Editor Tooling and Debugging

Docs (1.20 manual): `input-actions-editor-window-reference`, `Debugging`, `the-input-debugger-window`, `device-simulation`, `Testing`. The test suite itself: `qa-automation-engineer`.

## Input Actions Editor
The Properties panel changes shape by selection (action: type, Interactions, Processors; binding: path, groups), so a setting can look missing.

## Input Debugger
| Section | Settles |
|---|---|
| Devices | What is connected now, including hardware with no matching layout ("controller does nothing") |
| Layouts | Whether a custom/HID layout registered |
| Actions | Play mode only, once something is enabled; empty = never enabled |
| Users | Each user's scheme, paired devices, bound actions: wrong-player pairing shows here |
| Settings and metrics | Live settings of the running player, not the asset |

An asset that looks correct and an action that never fires are consistent; only the runtime view distinguishes them.

## Device Simulator and testing
- Device Simulator turns pointer input into simulated touch on a virtual touchscreen (Unity Remote is unsupported).
- It disables the real mouse and pen while running; close it if an unrelated Editor workflow seems broken.
- The package's test fixture base class synthesises device state for tests without hardware.
- Make the input layer testable behind an abstraction; the suite belongs to `qa-automation-engineer`.
