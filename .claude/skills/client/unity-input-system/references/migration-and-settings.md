# Migration, Project Settings & Known Limitations

[Manual — Migrate from the old input system](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/migrate-from-old-input-system.html) · [Enable the correct input system](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/enable-correct-input-system.html) · [Manual — Input settings](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/input-settings.html) · [Update Mode](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/update-mode.html) · [Manual — Known limitations](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/KnownLimitations.html)

## Active Input Handling — the project setting that decides which system runs

**Location**: `Edit → Project Settings → Player → Other Settings → Active Input Handling`.

| Setting | Effect |
|---|---|
| `Input Manager (Old)` | Only the legacy backend (`UnityEngine.Input`, `Input.GetKey`/`GetAxis`) is active. |
| `Input System Package (New)` | Only this package's backend is active — the legacy `UnityEngine.Input` API stops receiving events. |
| `Both` | Both backends run simultaneously; distinguish code paths with the compilation symbols `ENABLE_INPUT_SYSTEM` and `ENABLE_LEGACY_INPUT_MANAGER`. |

`Both` is a deliberate coexistence/migration mode, not a "just leave it on to be safe" default — running both continuously has real overhead and doubles the input surface a bug could hide in. Set it to `Input System Package (New)` once a project has fully migrated, per this project's KISS principle.

## Migration guidance — don't just API-map

[migrate-from-old-input-system.html](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/migrate-from-old-input-system.html) provides a table matching old `UnityEngine.Input` calls to new equivalents, but explicitly warns that the "directly corresponding API" is often "the quickest — but least flexible — solution." Read the Concepts/Workflows references first ([architecture-and-update-loop.md](architecture-and-update-loop.md), [actions-bindings-and-assets.md](actions-bindings-and-assets.md)) and design around Actions rather than mechanically replacing every `Input.GetAxis("Horizontal")` with the nearest single-line equivalent — a 1:1 API swap throws away rebinding, composite bindings, and control-scheme device matching that the new system exists to provide.

## `InputSettings` — project-wide configuration

Configured via a settings asset (Project Settings → Input System Package), covering (see [architecture-and-update-loop.md](architecture-and-update-loop.md) for Update Mode detail):

- **Update Mode** — `ProcessEventsInDynamicUpdate` / `ProcessEventsInFixedUpdate` / `ProcessEventsManually`.
- **Background behavior** — whether devices keep processing input while the app is unfocused/backgrounded (tied to `Application.runInBackground` — see Known Limitations below).
- **Compensate orientation** — auto-adjusts sensor readings (accelerometer/gyroscope) for the device's current screen orientation.
- **Default value properties** — the project-wide default deadzone values Processors fall back to (see [interactions-and-processors.md](interactions-and-processors.md)).
- **Supported devices / platform-specific settings** — restrict which device layouts the project cares about, trimming unused device support from builds.

## Known Limitations (as documented at package version 1.20 — verify against the live page for the installed version before relying on any of these long-term)

[KnownLimitations.html](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/KnownLimitations.html):

- Background input processing is tied to `Application.runInBackground`; a development Player always processes input even while backgrounded on supported platforms.
- **`PlayerInput` split-screen is incompatible with Cinemachine virtual cameras** — relevant if a split-screen local-multiplayer feature also wants Cinemachine-driven per-player cameras; flag this conflict early rather than discovering it after both systems are wired up.
- The Input System **cannot feed IMGUI** (`OnGUI`) at all.
- UI Toolkit currently supports only pointer (mouse/pen/touch) and gamepad input through this system, and requires an `EventSystem` to be present.
- After first enabling, UI won't react to pointer position until the pointer actually moves once.
- **Text input cannot be routed into uGUI or TextMesh Pro** components through the new system — text fields still need the legacy input path for actual character entry.
- UI does not "consume" input the way the old system's `Input.GetButtonDown` semantics implied — a click on a UI button and a simultaneous in-game action bound to the same control can both fire; don't assume UI interaction alone suppresses gameplay actions without an explicit check.
- Devices that lose OS focus don't automatically resync their state when focus returns — a key held down before focus loss won't be seen as "still held" after; the player must physically re-press it.
- Desktop platforms cannot distinguish between multiple simultaneous pointers or multiple keyboards as separate devices.
- Windows Pen input requires "Windows Ink" support enabled for Wacom-brand devices specifically.
- **HID input is not supported in 32-bit Players** — affects HID-class controllers (e.g. PS4 controllers on a 32-bit build target).
- Android exposes only a single `Touchscreen` device system-wide.
- Joy-Con controllers are only supported natively on Nintendo Switch.
- PS4 controller sensor data (motion/gyro) only works when actually running on PS4 hardware.
- Unity Remote does not currently support the Input System — mobile-device-in-Editor testing for this package uses the Device Simulator instead (see [editor-tooling-and-debugging.md](editor-tooling-and-debugging.md)), not Unity Remote.

Treat this list as a set of concrete, currently-real gaps to check a feature against before promising cross-device/cross-platform behavior — not a historical curiosity. Re-verify against the live `KnownLimitations.html` page for whatever package version the project actually has installed, since entries are added/resolved across releases.
