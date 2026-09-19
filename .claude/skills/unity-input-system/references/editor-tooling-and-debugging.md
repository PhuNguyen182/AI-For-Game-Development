# Editor Tooling and Debugging — Actions Editor, Input Debugger, Device Simulator

Sources: [Input Actions Editor window reference](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/input-actions-editor-window-reference.html), [Debugging](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/Debugging.html), [The input debugger window](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/the-input-debugger-window.html), [Device simulation](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/device-simulation.html), [Testing](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/Testing.html).
Covers: SKILL.md §4 — **"Take a non-firing action to the Input Debugger before re-reading the asset"**.

The windows that show what is actually happening at runtime, as opposed to
what the asset declares. Writing the test suite itself is
`qa-automation-engineer`'s work once the code has passed review.

## Input Actions Editor

| Panel | What it holds | Source |
|---|---|---|
| Action Maps | The maps in the asset, and the unit that gets enabled and disabled together | [Input Actions Editor window reference](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/input-actions-editor-window-reference.html) |
| Actions | Every action in the selected map with its bindings nested underneath | [Input Actions Editor window reference](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/input-actions-editor-window-reference.html) |
| Properties | Whatever is selected — an action's type, Interactions and Processors, or a binding's path and groups; the panel changes shape depending on which, which is why a setting can appear missing | [Input Actions Editor window reference](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/input-actions-editor-window-reference.html) |

## Input Debugger

| Section | What it settles | Source |
|---|---|---|
| Devices | Which devices are connected right now, including hardware Unity could not match to a layout — the answer to "the controller does nothing" | [The input debugger window](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/the-input-debugger-window.html) |
| Layouts | The registered layout database, for confirming a custom or HID layout actually registered | [The input debugger window](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/the-input-debugger-window.html) |
| Actions | Visible only in Play mode and only once something is enabled — its emptiness is itself the finding when an action was never enabled | [The input debugger window](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/the-input-debugger-window.html) |
| Users | Each input user's control scheme, paired devices and bound actions, which is where a wrong-player pairing becomes visible | [The input debugger window](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/the-input-debugger-window.html) |
| Settings and metrics | The live settings the running player is using, rather than the asset someone edited | [The input debugger window](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/the-input-debugger-window.html) |

**Critical caveat**: binding resolution depends on which devices are actually
connected and paired at runtime. An asset that looks correct and an action
that never fires are consistent with each other, and only the runtime view
distinguishes them.

## Device Simulator and testing

| Subject | What it decides | Source |
|---|---|---|
| Device Simulator | Converts pointer input into simulated touch and creates a virtual touchscreen, which is how touch code is tested without hardware since Unity Remote does not support this package | [Device simulation](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/device-simulation.html) |
| Native pointer suppression | The simulator disables the real mouse and pen while it runs, so an unrelated Editor workflow appears broken until the window is closed | [Device simulation](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/device-simulation.html) |
| Test fixture | The package's own test base class synthesises device state, which is what makes input-dependent tests possible without hardware | [Testing](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/Testing.html) |
| Testability boundary | This skill's job is making the input layer testable behind an abstraction; the suite that exercises it belongs to `qa-automation-engineer` | [Testing](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/Testing.html) |
