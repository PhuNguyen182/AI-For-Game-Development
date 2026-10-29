---
name: unity-input-system
description: "Input System: .inputactions assets, action types, composites, Interactions, Processors, control schemes, PlayerInput/PlayerInputManager, InputSystemUIInputModule, rebinding, on-screen touch. Use for any player input."
user-invocable: false
---

# Unity Input System

Not for: what a press means as a game rule (`csharp-engineer`), UI layout (`gameplay-engineer`), Animator parameters (`unity-animation`), camera axis controllers (`unity-cinemachine-authoring`), click-to-move pathing (`unity-navmesh-navigation`), the per-tick command struct of a predicted netcode simulation (`netcode-for-entities`), XR Interaction Toolkit and XR rendering (no owning skill: flag the gap).
Docs: https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/ — pinned 1.20; slugs are stable nearby, substitute the version in `Packages/manifest.json`.

| Reference | Read when |
|---|---|
| [migration-and-settings.md](references/migration-and-settings.md) | First touch of the project (Active Input Handling unknown), a legacy `UnityEngine.Input` project, a missed or double-counted press (Update Mode), or before promising a platform feature |
| [actions-bindings-and-assets.md](references/actions-bindings-and-assets.md) | Authoring actions, composites, Control Schemes, Interactions or Processors; a correctly bound action never performs |
| [player-input-and-multiplayer.md](references/player-input-and-multiplayer.md) | More than one local player, or a `PlayerInput` is already in the scene |
| [devices-and-ui-integration.md](references/devices-and-ui-integration.md) | Wiring UI, on-screen touch controls, or reading a device without an action |
| [rebinding.md](references/rebinding.md) | Players change their own controls |
| [editor-tooling-and-debugging.md](references/editor-tooling-and-debugging.md) | An action does not fire, the wrong device is paired, or touch must be tested without hardware |

## Steps
1. **Confirm Active Input Handling first** — the API is inert under the legacy backend; such a task is a migration question. See [migration-and-settings.md](references/migration-and-settings.md).
2. **Author actions in the `.inputactions` asset**, not in code — the editor, generated wrapper, rebinding and Debugger all read it. Script construction only when the set is unknown until runtime.
3. **Pick the action type from the control** — `Button` for discrete intents (a jump authored as `Value` fires every frame it is held), `Value` for continuous input, `PassThrough` only to aggregate sources.
4. **Use a composite for multi-control input** — one 2D Vector composite makes WASD and a stick the same `Move`; set its mode explicitly or keyboard diagonals outrun the stick.
5. **Add an Interaction only for a real timing pattern**; one the player never performs means the action never fires. Check the project default deadzones before adding a Processor that duplicates them. See [actions-bindings-and-assets.md](references/actions-bindings-and-assets.md).
6. **Set the Update Mode from where the logic runs** — dynamic for `Update`, fixed for physics movement in `FixedUpdate`. Reading one action from both sees different lifecycle points; use the frame-scoped pressed/released queries ([migration-and-settings.md](references/migration-and-settings.md)).
7. **Pick the consumption workflow** — generated wrapper or action polling for one player; `PlayerInput` only when its pairing and per-player machinery is wanted; raw device polling only for a prototype or a fixed single-platform scheme (forfeits rebinding, composites, deadzones; null-check every read).
8. **`PlayerInput` notification = Invoke C# Events**, never Send/Broadcast Messages (`SendMessage` is banned by rule `csharp.md`; handler names derive from the action name, so a rename breaks them silently). Details in [player-input-and-multiplayer.md](references/player-input-and-multiplayer.md).
9. **Enable what you read; cache the reference** — resolve once in `Awake`/`OnEnable`, disable and unsubscribe in `OnDisable`; never look up by string per frame. An action never enabled returns its default value silently.
10. **Hand gameplay an interface** (`IInputProvider`-style) so `Game.Core.*` stays free of `UnityEngine` and testable; input code reports that a press happened, `Game.Core.*` decides what it means.
11. **Drive UI through `InputSystemUIInputModule`** on the scene `EventSystem`, per [devices-and-ui-integration.md](references/devices-and-ui-integration.md); check both the module and the project-wide UI map before blaming the asset.
12. **Dispose each `RebindingOperation`** and key saved overrides per player, per [rebinding.md](references/rebinding.md).
13. **Non-firing action: open the Input Debugger in Play mode before re-reading the asset** — resolution depends on devices connected and paired at runtime, per [editor-tooling-and-debugging.md](references/editor-tooling-and-debugging.md).
14. **Check the documented gaps before promising** (text entry into uGUI, IMGUI, split-screen with Cinemachine), per [migration-and-settings.md](references/migration-and-settings.md).

## Never
- Store an `InputAction.CallbackContext` or `InputValue` past the callback — it returns plausible, wrong data.
- Call the non-generic `InputValue` accessor in a hot path — it boxes.
- Enable or disable a map directly while a `PlayerInput` owns it — they desynchronise.
- Assume a UI click suppresses a gameplay action on the same control — both fire.
- Use obsolete tracked-pose-driver action properties in new code (`csharp-standards` → `coding-principles.md` Obsolete APIs).

## Output
```
## Input Work — <feature>
- Active Input Handling: <New / Both> — legacy involvement
- Workflow: <wrapper / polling / PlayerInput / raw device> — why
- Actions: <asset, maps, action types, bindings, Interactions/Processors and why>
- Update Mode: <dynamic / fixed / manual>
- Multiplayer / rebinding: <joining, pairing, split-screen, persistence key — or "not applicable">
- Abstraction and lifecycle: <interface; enable/disable/dispose sites; PlayerInput notification = Invoke C# Events (not Send/Broadcast); no gameplay outcome decided in input code>
- Platform gaps checked: <relevant entries — or "none apply">
- Known limitations: <...>
```
On request only, add `Latent concerns` and `Future remediation`, each with its trigger.

## Example
- "Use Send Messages on `PlayerInput`, it is the default" → declined: reflection dispatch banned by `csharp.md`, and renaming `Fire` to `Attack` silently stops the handler; switched to Invoke C# Events with a named method unsubscribed in `OnDisable`.
