# PlayerInput and Local Multiplayer

Docs (1.20 manual): `player-input-component`, `select-notification-behavior`, `device-assignments`, `player-input-manager-component`, `set-up-split-screen-local-multiplayer`. Camera half of split-screen: `unity-cinemachine-authoring` / `unity-camera-fundamentals`; UI layout: `gameplay-engineer`.

## What the component owns
- A private copy of the action asset: binding overrides on one player do not reach another.
- Current action map, tracked only through its own switch method; enabling/disabling the underlying map directly desynchronises it.
- Paired devices, player index and viewport camera.

## Notification behaviours
| Behaviour | Verdict |
|---|---|
| Send Messages | Banned (`SendMessage`, rule `csharp.md`); handler name derives from the action name, so a rename breaks it with no compile error |
| Broadcast Messages | Same, propagated down the hierarchy, costlier |
| Invoke Unity Events | Acceptable where Inspector wiring is wanted and handler lifetime is scoped |
| Invoke C# Events | Project default: no reflection, rename is a compile error |

The message behaviours can be the Inspector default, so they appear in existing projects. Presence is a review finding, not an accepted exception.

## Callback data
- `InputValue` is valid only inside its callback.
- The generic read returns a struct without allocation; the untyped one boxes.

## Several local players
- `PlayerInputManager` creates/destroys `PlayerInput` on join/leave and owns device-to-player pairing.
- Join behaviour (button press, action, manual) decides whether an idle controller can claim a slot by accident.
- Split-screen: enable on the manager, assign a camera on the player prefab; viewports are sized automatically.
- Isolate each player's UI to its own event system and camera, or every player drives every menu (never reported as an error).
- The package's multiplayer sample demonstrates joining, pairing and split-screen end to end.
