# Migration and Settings — Active Input Handling, InputSettings, documented gaps

Sources: [Enable the correct input system](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/enable-correct-input-system.html), [Migrate from the old input system](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/migrate-from-old-input-system.html), [Input settings](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/input-settings.html), [Known limitations](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/KnownLimitations.html).
Covers: SKILL.md §4 — **"Confirm Active Input Handling before citing a single API"**, **"Check the feature against the package's documented gaps before promising it"**.

What has to be true of the project before any API in this package runs, and
the list of things the package documents as not working. Anything on the gap
list is a constraint to design around, not a bug to fix here; the XR
Interaction Toolkit surface named at the end has no owner in this project.

## Active Input Handling

Location: `Edit → Project Settings → Player → Other Settings → Active Input Handling`.

| Setting | Effect | Source |
|---|---|---|
| Input Manager (Old) | Only the legacy backend runs, so every API in this package is inert — a task on such a project is a migration question rather than an authoring one | [Enable the correct input system](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/enable-correct-input-system.html) |
| Input System Package (New) | Only this package runs, and the legacy `UnityEngine.Input` API stops receiving events entirely | [Enable the correct input system](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/enable-correct-input-system.html) |
| Both | Both backends run at once, distinguished in code by the `ENABLE_INPUT_SYSTEM` and `ENABLE_LEGACY_INPUT_MANAGER` symbols — a migration mode with real overhead, not a safe default to leave set | [Enable the correct input system](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/enable-correct-input-system.html) |

## Migration approach

| Subject | What it decides | Source |
|---|---|---|
| The API mapping table | Exists, and the Manual itself calls the direct swap the least flexible option — a one-to-one replacement of each legacy call discards rebinding, composites, and control-scheme matching, which is the reason to migrate at all | [Migrate from the old input system](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/migrate-from-old-input-system.html) |
| Migration unit | Migrate a feature's input model, not a call site — the legacy axis name and the new action rarely correspond one to one once composites and schemes exist | [Migrate from the old input system](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/migrate-from-old-input-system.html) |

## InputSettings

| Setting | What it decides | Source |
|---|---|---|
| Update Mode | Whether events are processed on the dynamic frame, the fixed step, or only when a script asks — see [architecture-and-update-loop.md](architecture-and-update-loop.md) | [Input settings](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/input-settings.html) |
| Background behaviour | Whether devices keep producing input while the application is unfocused, tied to the run-in-background player setting | [Input settings](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/input-settings.html) |
| Default deadzone values | The project-wide fallback every stick and axis Processor uses; check this before adding a per-binding deadzone that duplicates or fights it | [Input settings](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/input-settings.html) |
| Compensate orientation | Whether sensor readings are adjusted for the current screen orientation, which silently changes accelerometer axes if left unconsidered | [Input settings](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/input-settings.html) |
| Supported devices | Restricts which device layouts the project builds support for, trimming unused device code out of the player | [Input settings](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/input-settings.html) |

## Documented gaps

| Gap | Consequence for a promise | Source |
|---|---|---|
| No IMGUI support | Editor-style immediate-mode UI cannot be driven by this package at all | [Known limitations](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/KnownLimitations.html) |
| No text entry into uGUI or TextMesh Pro | Character input into a text field still needs the legacy path, so a project set to the new backend alone cannot type into one | [Known limitations](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/KnownLimitations.html) |
| UI does not consume input | A pointer click on a UI button and a gameplay action bound to the same control both fire; suppressing one is an explicit check, not automatic | [Known limitations](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/KnownLimitations.html) |
| Split-screen `PlayerInput` and Cinemachine | Documented as incompatible — surface it while the feature is being designed, and route the camera half to `unity-cinemachine-authoring` | [Known limitations](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/KnownLimitations.html) |
| No state resync after focus loss | A key held while the app loses focus is not seen as held when focus returns; the player must press it again | [Known limitations](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/KnownLimitations.html) |
| One touchscreen device on Android | Multiple physical touch surfaces are not separable there | [Known limitations](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/KnownLimitations.html) |
| No multiple pointers or keyboards on desktop | Two mice or two keyboards cannot be told apart as separate devices | [Known limitations](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/KnownLimitations.html) |
| No HID support in 32-bit players | HID-class controllers do not appear at all on a 32-bit build target | [Known limitations](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/KnownLimitations.html) |
| Unity Remote unsupported | In-Editor mobile testing uses the Device Simulator instead — see [editor-tooling-and-debugging.md](editor-tooling-and-debugging.md) | [Known limitations](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/KnownLimitations.html) |

**Critical caveat**: this list is versioned. Re-read the live page for the
package version the project actually installs before committing a design to
any entry here, since items are both added and resolved between releases.
