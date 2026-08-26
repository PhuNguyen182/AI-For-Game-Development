# PlayerInput and Local Multiplayer — notification behaviours, pairing, split-screen

Sources: [Player Input component](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/player-input-component.html), [Select a notification behavior](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/select-notification-behavior.html), [Device assignments](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/device-assignments.html), [Player Input Manager component](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/player-input-manager-component.html), [Set up split-screen local multiplayer](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/set-up-split-screen-local-multiplayer.html), [PlayerInput API](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/api/UnityEngine.InputSystem.PlayerInput.html).
Covers: SKILL.md §4 — **"Set `PlayerInput` to Invoke C# Events, never Send or Broadcast Messages"**.

What `PlayerInput` adds over plain actions, which of its four dispatch modes
this project permits, and how several local players are wired. The camera
half of a split-screen feature is `unity-cinemachine-authoring`'s or
`unity-camera-fundamentals`', and its UI layout is `ui-ux-programmer`'s.

## What the component owns

| Subject | What it decides | Source |
|---|---|---|
| Its own asset copy | Each `PlayerInput` holds a private copy of the action asset, so binding overrides applied to one player do not reach another | [Player Input component](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/player-input-component.html) |
| Current action map | Tracked only through its own switch method; enabling or disabling the underlying map directly desynchronises the component from reality | [PlayerInput API](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/api/UnityEngine.InputSystem.PlayerInput.html) |
| Paired devices | Which physical devices belong to this player, so gameplay code never asks which gamepad it is reading | [Device assignments](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/device-assignments.html) |
| Player index and camera | The identity and viewport a split-screen setup assigns per joined player | [Set up split-screen local multiplayer](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/set-up-split-screen-local-multiplayer.html) |

## Notification behaviours

| Behaviour | Mechanism | Verdict | Source |
|---|---|---|---|
| Send Messages | Reflection dispatch on the component's own object, with the handler name derived from the action name | Banned by `performance-and-algorithms.md`; a renamed action breaks the handler with no compile error | [Select a notification behavior](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/select-notification-behavior.html) |
| Broadcast Messages | The same reflection dispatch, propagated down the whole hierarchy | Banned for the same reason, and more expensive again | [Select a notification behavior](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/select-notification-behavior.html) |
| Invoke Unity Events | One serialized event per notification, wired in the Inspector | Acceptable where Inspector wiring is genuinely wanted and the handler lifetime is scoped | [Select a notification behavior](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/select-notification-behavior.html) |
| Invoke C# Events | Plain events on the component, subscribed in code | The default for this project — no reflection, and a rename is a compile error | [Select a notification behavior](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/select-notification-behavior.html) |

**Critical caveat**: the message behaviours are the Inspector's own default in
some setups, which is why they appear in existing projects. Their presence is
a finding in review, not an accepted exception.

## Callback data lifetime

| Subject | What it decides | Source |
|---|---|---|
| `InputValue` validity | Valid only inside the callback it was handed to; stored and read afterwards it returns wrong results with no error | [Player Input component](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/player-input-component.html) |
| Typed versus untyped read | The generic read returns a struct with no allocation; the untyped one boxes, so it is a per-call allocation in whatever loop calls it | [Player Input component](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/player-input-component.html) |

## Several local players

| Subject | What it decides | Source |
|---|---|---|
| `PlayerInputManager` | Creates and destroys `PlayerInput` instances as players join and leave, and owns device-to-player pairing so gameplay code never does | [Player Input Manager component](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/player-input-manager-component.html) |
| Join behaviour | Join on button press, on action, or manually — the choice decides whether an idle controller can claim a slot by accident | [Player Input Manager component](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/player-input-manager-component.html) |
| Split-screen | Enabled on the manager, with a camera assigned on the player prefab; viewports are then sized and positioned automatically | [Set up split-screen local multiplayer](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/set-up-split-screen-local-multiplayer.html) |
| Per-player UI | Without isolating each player's UI to its own event system and camera, every player can drive every player's menu — rarely the intent, and never reported as an error | [Set up split-screen local multiplayer](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/set-up-split-screen-local-multiplayer.html) |
| Multiplayer sample | Ships with the package and demonstrates joining, pairing and split-screen end to end — a better starting point than re-deriving the flow | [Player Input Manager component](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/player-input-manager-component.html) |
