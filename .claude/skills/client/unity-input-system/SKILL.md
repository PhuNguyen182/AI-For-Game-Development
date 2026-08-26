---
name: unity-input-system
description: >
  Technique for Unity's Input System package (`UnityEngine.InputSystem`) —
  `InputAction`, `InputActionAsset`, `InputActionMap`, action types, bindings
  and composite bindings, Interactions and Processors, Control Schemes,
  `PlayerInput` notification behaviours, `PlayerInputManager` split-screen,
  `InputSystemUIInputModule`, `Gamepad.current` device polling,
  `OnScreenButton` and `OnScreenStick`, interactive rebinding and binding
  overrides, and the Active Input Handling setting. Use when player input must
  be read, bound, rebound, or routed into UI. Not for: what a press means as a
  game rule (`csharp-engineer`); UI layout (`ui-ux-programmer`); Animator
  parameters (`unity-animation`); camera axis controllers
  (`unity-cinemachine-authoring`); XR Interaction Toolkit and XR rendering
  (no owning skill — flag the gap).
---

# Unity Input System — Actions, Bindings, PlayerInput, Rebinding, UI Input

## Bundled resources

### References
Read-only context, loaded on demand so SKILL.md itself stays short.

| File | Contents | Read when |
|---|---|---|
| [root-links.md](references/root-links.md) | Manual and API roots, the package version pin, the core type index | Starting any task here, or confirming the installed package version |
| [migration-and-settings.md](references/migration-and-settings.md) | Active Input Handling, `InputSettings`, and the documented platform gaps | Before the first API call, and before promising any cross-platform behaviour |
| [actions-bindings-and-assets.md](references/actions-bindings-and-assets.md) | Action assets, project-wide actions, generated wrapper, action types, composites, Control Schemes | Authoring or editing what the player can do |
| [interactions-and-processors.md](references/interactions-and-processors.md) | Built-in Interactions with their phase behaviour, Processors, default deadzones | A gesture or a value shape has to be recognised or transformed |
| [architecture-and-update-loop.md](references/architecture-and-update-loop.md) | Device to control to action pipeline, Update Modes, timing and latency | Input and physics disagree, or a press is missed or double-counted |
| [player-input-and-multiplayer.md](references/player-input-and-multiplayer.md) | `PlayerInput`, the four notification behaviours, `InputValue`, `PlayerInputManager`, split-screen | More than one local player, or a `PlayerInput` is already in the scene |
| [devices-and-ui-integration.md](references/devices-and-ui-integration.md) | Device categories, direct polling, `InputSystemUIInputModule`, on-screen controls, the XR boundary | Wiring UI, touch controls, or reading a device without an action |
| [rebinding.md](references/rebinding.md) | `PerformInteractiveRebinding`, binding overrides, saving and loading them | Players change their own controls |
| [editor-tooling-and-debugging.md](references/editor-tooling-and-debugging.md) | Input Actions Editor, Input Debugger, Device Simulator, test fixture | An action does not fire, or the wrong device got paired |

## 1. Objective
Turn device input into signals the rest of the game can consume, rebind, and test. Almost every failure here is silent: an action that was never enabled reads its default value forever, an Interaction whose gesture the player never performs never reaches `Performed`, a composite left on its default mode changes diagonal speed between keyboard and stick, a `CallbackContext` stored and read later returns something plausible and wrong, and a `PlayerInput` message handler breaks the moment its action is renamed — with no compile error in any of those cases.

## 2. Role
Act as the input specialist for the client track — the tool reached for whenever a feature needs to know what the player is doing. You supply the signal and the plumbing around it; you never decide what the signal means for the game state, and you stop at the point input reaches a UI callback, an Animator parameter, or a camera axis.

## 3. When to invoke this skill
- Authoring or editing an `.inputactions` asset: action maps, actions, bindings, composites, Interactions, Processors, Control Schemes.
- Deciding how game code consumes input — generated wrapper class, direct action polling, `PlayerInput`, or raw device reads.
- Local multiplayer: joining, device pairing, split-screen viewports, per-player UI isolation.
- Runtime rebinding and persisting the result per player.
- Touch controls, or wiring a scene's `EventSystem` so UI responds to gamepad and pointer input.
- Migrating from the legacy `UnityEngine.Input` API, or deciding the Active Input Handling setting.
- An action does not fire, fires twice, or the wrong device drives it.
- Negative trigger: whether the action the player just requested is currently allowed — cooldown, resource cost, stun — that is `csharp-engineer`'s Shared Core, per `coding-principles.md`'s Shared Core integrity rule; this skill reports only that the input happened.
- Negative trigger: the Canvas hierarchy, widget design, or screen layout the UI module ends up driving — that is `ui-ux-programmer`; this skill stops at the input module and its action map.
- Negative trigger: the Animator parameters or blend trees a movement value feeds — that is `unity-animation`; this skill delivers the value.
- Negative trigger: a Cinemachine camera that does not respond to a stick — the axis controller component belongs to `unity-cinemachine-authoring`, which this skill feeds; the binding behind it is this skill's.
- Negative trigger: destination and pathfinding decisions behind a click-to-move gesture — that is `unity-navmesh-navigation`; this skill supplies the screen position.
- Negative trigger: XR rendering configuration or the XR Interaction Toolkit package — raw tracked-device input is a boundary case here and nothing beyond it is; no skill in this project owns that surface, so say so rather than improvising.

## 4. How to use this skill
1. **Confirm Active Input Handling before citing a single API** — this package's API does nothing while the project is set to the legacy backend, and a task about `Input.GetAxis` on such a project is a migration question rather than an authoring one, per [migration-and-settings.md](references/migration-and-settings.md) and the version pin in [root-links.md](references/root-links.md).
2. **Author actions in the `.inputactions` asset rather than in code** — the asset is what the Input Actions Editor, the generated wrapper, the rebinding API and the Debugger all read, per [actions-bindings-and-assets.md](references/actions-bindings-and-assets.md). Build actions from script only where the set genuinely is not known until runtime.
3. **Pick the action type from what the control produces** — `Button` performs once when the press crosses its point, `Value` performs continuously while actuated and resolves competing controls to the most actuated one, and `PassThrough` reports every bound control independently with no resolution at all. A jump authored as `Value` fires every frame it is held.
4. **Express multi-control input as a composite binding rather than several actions** — one 2D Vector composite is what makes WASD and a stick the same `Move` action, and its mode decides whether a diagonal is normalised, which is why keyboard and stick otherwise move at different speeds.
5. **Add an Interaction only when a timing pattern is genuinely required** — an Interaction changes when the action reaches its phases, so one applied to a gesture the player never performs means the action never fires at all, per [interactions-and-processors.md](references/interactions-and-processors.md). Check the project's default deadzones before adding a Processor that duplicates them.
6. **Set the Update Mode from where the input-driven logic actually runs** — dynamic for logic in `Update`, fixed for physics-driven movement in `FixedUpdate`, per [architecture-and-update-loop.md](references/architecture-and-update-loop.md). Reading one action from both callbacks in the same frame sees it at different points in its lifecycle.
7. **Choose the consumption workflow from what the feature needs** — the generated wrapper or direct action polling for a single player, `PlayerInput` when its device-pairing and per-player machinery is actually wanted, and raw device polling only for a prototype or a fixed single-platform scheme, since it forfeits rebinding, composites and deadzones outright.
8. **Set `PlayerInput` to Invoke C# Events, never Send or Broadcast Messages** — both message behaviours are literally the reflection dispatch `performance-and-algorithms.md` bans, and their handler names derive from the action name, so renaming an action breaks them with no compile error. See [player-input-and-multiplayer.md](references/player-input-and-multiplayer.md) for the full comparison.
9. **Enable what you intend to read, and cache the reference you read it from** — an action that was never enabled returns its default value silently and forever, and a per-frame lookup by string is the hot-path cost `performance-and-algorithms.md` forbids. Resolve once in `Awake` or `OnEnable`, and disable and unsubscribe in `OnDisable`.
10. **Hand gameplay an interface rather than an Input System type** — an `IInputProvider`-style abstraction exposing resolved signals keeps `Game.Core.*` free of `UnityEngine` and testable by `qa-automation-engineer`, per Dependency Inversion in `coding-principles.md`. The interface is also what lets the decision behind a press stay in Shared Core.
11. **Drive UI through `InputSystemUIInputModule` on the scene's `EventSystem`** — it replaces the legacy standalone module and feeds uGUI and UI Toolkit alike, per [devices-and-ui-integration.md](references/devices-and-ui-integration.md). A module present in the scene takes precedence over the project-wide asset's UI map, so check both before concluding the asset is wrong.
12. **Dispose the `RebindingOperation` and key saved overrides per player** — it is `IDisposable` and is not cleaned up for you, per `coding-principles.md`'s Exception handling section, and loading overrides clears the existing ones unless told otherwise, per [rebinding.md](references/rebinding.md).
13. **Take a non-firing action to the Input Debugger before re-reading the asset** — binding resolution depends on which devices are actually connected and paired at runtime, which the asset cannot show, per [editor-tooling-and-debugging.md](references/editor-tooling-and-debugging.md).
14. **Check the feature against the package's documented gaps before promising it** — text entry into uGUI, IMGUI, split-screen alongside Cinemachine, and several device and platform combinations are documented limitations rather than bugs, per [migration-and-settings.md](references/migration-and-settings.md).

## 5. Specific goals / tasks this skill performs
- Authoring `.inputactions` assets: maps, actions, action types, bindings, composites, Interactions, Processors, Control Schemes.
- Generating and wiring the typed C# wrapper, or configuring the project-wide actions asset.
- Choosing and implementing the consumption workflow behind an `IInputProvider`-style abstraction.
- Configuring `PlayerInput` notification behaviour and `PlayerInputManager` joining, pairing and split-screen.
- Interactive rebinding, binding overrides, and per-player persistence.
- On-screen touch controls, and `InputSystemUIInputModule` setup on a scene's `EventSystem`.
- Deciding Active Input Handling and migrating legacy `UnityEngine.Input` call sites to actions.
- Diagnosing non-firing, double-firing, or wrongly paired input through the Input Debugger and Device Simulator.
- Out of scope: the game rule behind a press (`csharp-engineer`); UI layout and widget design (`ui-ux-programmer`); Animator parameters and blend trees (`unity-animation`); camera axis controllers and camera behaviour (`unity-cinemachine-authoring`); destination and pathfinding decisions (`unity-navmesh-navigation`); XR Interaction Toolkit and XR rendering (no owning skill — flag the gap).

## 6. Output format
```
## Input Work — <feature or character name>
- Active Input Handling: <Input System Package (New) / Both> — legacy involvement if any
- Consumption workflow: <generated wrapper / direct action polling / PlayerInput / raw device> — rationale
- Action asset: <name>, maps and actions touched, action type per action
- Bindings: <paths and composites> — Interactions and Processors applied, and why each
- Update Mode: <dynamic / fixed / manual> — and where the input-driven logic runs
- PlayerInput behaviour: <Invoke C# Events / Invoke Unity Events> — confirmed not Send or Broadcast Messages
- Multiplayer: <join behaviour, pairing, split-screen and per-player UI isolation — or "single player">
- Rebinding: <interactive setup, persistence key, operation disposal — or "not applicable">
- Abstraction: <interface introduced or reused, or why none was needed>
- Lifecycle: <enable, disable, unsubscribe and dispose call sites confirmed>
- Shared Core boundary: confirmed no gameplay outcome decided in input-layer code
- Platform gaps checked: <documented limitations relevant to this feature — or "none apply">
- Layer: Game.Client.* — Game.Core.* sees only the abstraction
- Known limitations: <...>
```

**Extended report — emit ONLY when the requester asks for it.** It replaces the one-line `Known limitations` above with all three fields:
```
- Known limitations: <what the delivered input setup does not cover>
- Latent concerns: <failure modes not yet triggered: device classes untested, platform gaps not yet hit, trade-offs knowingly deferred>
- Future remediation: <the concrete fix for each concern above, each with the condition that should trigger it>
```

## 7. Examples
**Example 1**
- Input: "Wire up movement and jump for a single-player controller, kept testable and decoupled."
- Output: confirmed the project runs the new backend. Authored a `Player` map with `Move` as a `Value` action on a 2D Vector composite over WASD and the left stick, mode set explicitly so keyboard diagonals match stick magnitude, and a stick deadzone left to the project default rather than duplicated per binding. `Jump` is a `Button` — as a `Value` action it would have performed every frame it was held. Generated the C# wrapper, enabled the map in `OnEnable` and disabled it in `OnDisable`, and exposed both signals through an interface so Shared Core decides whether a jump is currently legal.

**Example 2**
- Input: "Use Send Messages on `PlayerInput`, it is the default and it works."
- Output: declined — Send Messages is `GameObject.SendMessage`, the reflection dispatch `performance-and-algorithms.md` bans, and its handler name is derived from the action name, so renaming `Fire` to `Attack` silently stops the handler with no compile error. Switched to Invoke C# Events, subscribed through a named method per `coding-principles.md`'s Event handlers rule, and unsubscribed in `OnDisable`.

**Example 3**
- Input: "The interact button does nothing, but the binding is right in the asset."
- Output: opened the Input Debugger in Play mode rather than re-reading the asset. The action resolved to its control correctly, but a Hold Interaction had been added to it, and the intended gesture was a tap — the action started and cancelled without ever performing. Removed the Interaction, since the design wanted an immediate press and the hold was left over from an earlier iteration.

**Example 4**
- Input: "Four-player split-screen co-op with Cinemachine cameras per player and a mid-game rebinding menu."
- Output: `PlayerInputManager` configured for gamepad joining with split-screen enabled, each player's UI isolated to its own camera so players cannot drive each other's menus, and rebinding built on the interactive API with an explicit cancel control, wrapped for disposal, and persisted per player index. Flagged the documented incompatibility between `PlayerInput` split-screen and Cinemachine before either was wired, and routed the camera side to `unity-cinemachine-authoring` with the constraint stated rather than discovered later.

## 8. Edge cases & guardrails
- Never read an action that was never enabled — it returns its default value silently, which reads as a dead binding rather than a lifecycle mistake.
- Never store an `InputAction.CallbackContext` or an `InputValue` and read it after the callback returns — both are valid only during the callback and return plausible, wrong data afterwards.
- Never call the non-generic value accessor on `InputValue` in a hot path — it boxes and allocates, per `performance-and-algorithms.md`.
- Never look an action up by string inside `Update` — cache the reference, or use the generated wrapper's typed property.
- Never set `PlayerInput` to Send or Broadcast Messages — reflection dispatch plus a handler name derived from the action name, so a rename breaks it silently.
- Never enable or disable a map directly while a `PlayerInput` owns it — its notion of the current map only tracks changes made through its own API, and the two desynchronise.
- Never assume a UI click suppresses the gameplay action bound to the same control — this system does not consume input the way the legacy one appeared to, so both fire.
- Never promise text entry into uGUI or TextMesh Pro, or any IMGUI input, through this package — both are documented limitations that still require the legacy path.
- Never wire `PlayerInput` split-screen and Cinemachine without surfacing the documented incompatibility first — it is cheaper to design around than to discover after both exist.
- Never author new code against the obsolete pose action properties on the tracked pose driver — use the current input properties, per `coding-principles.md`'s Obsolete APIs section.
- Never leave a `RebindingOperation` undisposed, and never load binding overrides without deciding whether the existing ones should survive.
- Never treat direct device polling as a production default — it forfeits rebinding, composites and deadzones, and needs a null check on every read.
- Never expand this skill into XR Interaction Toolkit or XR rendering — no skill in this project owns that surface; say so rather than improvising from Input System knowledge.
- Never let input-layer code decide a gameplay outcome — it reports what happened, and `Game.Core.*` decides what it means.
