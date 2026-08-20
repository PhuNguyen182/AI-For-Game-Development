# PlayerInput, Notification Behaviors & Local Multiplayer

[Manual — The Player Input component](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/player-input-component.html) · [About the Player Input component](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/about-player-input-component.html) · [Select a notification behavior](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/select-notification-behavior.html) · [Device Assignments](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/device-assignments.html) · [The Player Input Manager component](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/player-input-manager-component.html) · [Set up split-screen local multiplayer](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/set-up-split-screen-local-multiplayer.html) · [API — PlayerInput](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/api/UnityEngine.InputSystem.PlayerInput.html)

## `PlayerInput` — the per-player connection between devices, actions, and callbacks

`PlayerInput` represents one player: it owns a private copy of an `InputActionAsset` (`actions`), tracks the `currentActionMap`/`defaultActionMap`, the player's paired `devices`, and (in multiplayer) a `playerIndex` and optional `camera` for split-screen. Switching maps/schemes must go through its own methods — `SwitchCurrentActionMap(string)`, `SwitchCurrentControlScheme(...)` — rather than calling `Enable()`/`Disable()` directly on the underlying `InputActionMap`, because `PlayerInput.currentActionMap` only tracks changes made through its own API (see Edge cases in the main SKILL.md).

## Notification Behavior — the four dispatch modes, and this project's required choice

[select-notification-behavior.html](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/select-notification-behavior.html) documents `PlayerInput.notificationBehavior` (`PlayerNotifications` enum), configured in the Inspector's "Behavior" dropdown:

| Behavior | Mechanism | Notes |
|---|---|---|
| **Send Messages** | `GameObject.SendMessage()` on the `PlayerInput`'s own GameObject, method name derived from the action name (`OnMove`, `OnJump`, …). | **Reflection-based, string-name-derived dispatch.** |
| **Broadcast Messages** | `GameObject.BroadcastMessage()` down the entire GameObject hierarchy. | Same reflection mechanism as Send Messages, just propagated to children too. |
| **Invoke Unity Events** | One `UnityEvent` per notification, wired in the Inspector's Events foldout. Callback argument matches the `started`/`performed`/`canceled` callback signature. | Inspector-wireable, not reflection-based — a normal `UnityEvent` invocation. |
| **Invoke C# Events** | Plain C# events on the `PlayerInput` API: `onActionTriggered` (fires for every action), `onDeviceLost`, `onDeviceRegained`. | **Not Inspector-configurable** — subscribe in code. No reflection, no per-call name lookup. |

**This project's rule**: `performance-and-algorithms.md` explicitly bans `SendMessage`/`BroadcastMessage`/string-keyed `Invoke("MethodName", ...)` for dispatch — "an order of magnitude slower than a direct method call, interface call, or `UnityEvent`/`Action`." `PlayerInput`'s "Send Messages" and "Broadcast Messages" behaviors are **literally** `GameObject.SendMessage`/`BroadcastMessage` under the hood, so they are the banned pattern wearing an Inspector dropdown, not an exception to it. **Default this project's `PlayerInput` components to `Invoke C# Events`** (subscribed via a named method per `coding-principles.md`'s Event handlers rule, unsubscribed in `OnDisable()`), or **skip `PlayerInput` entirely and consume the generated C# wrapper class / raw `InputAction` callbacks directly** when `PlayerInput`'s device-pairing/multiplayer machinery isn't actually needed. `Invoke Unity Events` is an acceptable middle ground when a UI/designer-facing wiring point in the Inspector is genuinely useful and the handler's lifetime is scoped correctly — it isn't reflection-based, only `Send`/`Broadcast Messages` are.

Constants worth knowing if `Send`/`Broadcast Messages` is ever encountered in existing/legacy code being reviewed (not for new code): `PlayerInput.ControlsChangedMessage = "OnControlsChanged"`, `DeviceLostMessage = "OnDeviceLost"`, `DeviceRegainedMessage = "OnDeviceRegained"` — action-triggered messages derive their name from the action itself (`"On" + ActionName`), which means **renaming an action silently breaks a `SendMessage` handler with no compile error** — one more concrete argument for `Invoke C# Events` in this project.

## `InputValue` — the callback-context wrapper for message/UnityEvent style callbacks

`InputValue` (passed to `OnMove(InputValue value)`-style handlers under Send Messages/Invoke Unity Events) wraps the same data an `InputAction.CallbackContext` carries, "shield[ing] the receiver from having to know about action callback specifics." `Get<TValue>()` reads the value typed as a struct (no allocation); the non-generic `Get()` boxes the value and **allocates GC garbage** — never call it in a hot path. **The `InputValue` instance is only valid during the callback** — storing the reference and calling `Get<T>()` from outside the callback "does not work correctly," the same caching pitfall `InputAction.CallbackContext` has (see [actions-bindings-and-assets.md](actions-bindings-and-assets.md) and the main SKILL.md's guardrails).

## `PlayerInputManager` — joining/leaving and split-screen

[player-input-manager-component.html](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/player-input-manager-component.html): `PlayerInputManager` "automatically manages the creation and lifetime of `PlayerInput` instances as players join and leave the game" — the orchestration layer above individual `PlayerInput`s for local co-op. It handles device-to-player pairing (which gamepad belongs to which joined player) so gameplay code doesn't have to.

**Split-screen setup** ([set-up-split-screen-local-multiplayer.html](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/set-up-split-screen-local-multiplayer.html)):
1. Enable "Split-Screen" on the `PlayerInputManager`.
2. Assign a `Camera` reference on the `PlayerInput` prefab it instantiates per joining player.
3. `PlayerInputManager` automatically resizes/repositions each player's camera viewport — configurable via "Maintain Aspect Ratio," a fixed screen-rectangle count, or explicit screen rectangles.
4. For split-screen **UI**, restrict each screen-space UI to its own player's camera (`InputSystemUIInputModule` + `MultiplayerEventSystem`, see [devices-and-ui-integration.md](devices-and-ui-integration.md)) — by default all players can interact with any UI, which is very rarely the intended behavior in split-screen.

Sample project: "Simple Multiplayer" (installable via Package Manager samples) demonstrates a working `PlayerInputManager` setup end to end — prefer starting from it over re-deriving join/leave/pairing logic from scratch, consistent with this project's general "prefer the built-in, well-tested implementation" bias in `performance-and-algorithms.md`.
