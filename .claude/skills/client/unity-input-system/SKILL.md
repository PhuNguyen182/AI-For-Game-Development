---
name: unity-input-system
description: >
  Technique for Unity's Input System package (`com.unity.inputsystem`,
  namespace `UnityEngine.InputSystem`) — the modern, device-agnostic
  replacement for the legacy `UnityEngine.Input`/Input Manager. Covers the
  runtime architecture (native backend → event buffers → state buffers →
  `InputControl`/`InputDevice` hierarchy → `InputSystem` static hub, Update
  Modes Dynamic/Fixed/Manual, `InputSystem.Update()`), the Actions system
  (`InputActionAsset`, `InputActionMap`, `InputAction`, bindings, composite
  bindings — 1D Axis/2D Vector/3D Vector/One-Two Modifiers, Interactions —
  Press/Hold/Tap/SlowTap/MultiTap, Processors — Normalize/Invert/Scale/Clamp/
  StickDeadzone/AxisDeadzone, Control Schemes, action phases and
  `InputAction.CallbackContext`), the three consumption workflows (the
  `PlayerInput` component and its Send Messages/Broadcast Messages/Invoke
  Unity Events/Invoke C# Events behaviors, the generated C# wrapper class from
  an `.inputactions` asset, direct polling via `ReadValue<T>()`/
  `WasPressedThisFrame()`, and low-level device polling via `Gamepad.current`/
  `Keyboard.current`/`Mouse.current`), local multiplayer (`PlayerInputManager`,
  device pairing/joining, split-screen), runtime rebinding
  (`InputActionRebindingExtensions`, `PerformInteractiveRebinding`,
  `SaveBindingOverridesAsJson`/`LoadBindingOverridesFromJson`), device support
  (Gamepad, Keyboard, Mouse, Pen, Touchscreen, Joystick, Sensors, HID generic
  devices, raw XR/tracked device input, on-screen controls via
  `OnScreenButton`/`OnScreenStick`), UI integration
  (`InputSystemUIInputModule` replacing the legacy `StandaloneInputModule`,
  `EventSystem` setup), editor tooling (Input Actions Editor window, Input
  Debugger, Device Simulator, `.inputactions` asset format/C# class
  generation), and migration/coexistence with the legacy Input Manager
  (`Active Input Handling` project setting: Old/New/Both). Use this for any
  task touching `InputAction`, `InputActionAsset`, `InputActionMap`,
  `PlayerInput`, `PlayerInputManager`, `InputSystem.*` static calls,
  `Gamepad`/`Keyboard`/`Mouse`/`Touchscreen`.current, on-screen controls, or
  runtime rebinding — e.g. "wire up move/jump/attack input for the player
  controller", "add a 2D Vector composite binding for WASD and left-stick
  movement", "let players rebind their controls and save the result", "set up
  local split-screen co-op for up to 4 gamepads", "this project's PlayerInput
  is using Send Messages, is that okay for our performance rules", "add
  on-screen touch controls for mobile", "the UI doesn't respond to gamepad
  navigation, wire up the Input System UI module". Do not use this for the
  actual gameplay decision an input signal triggers — whether an attack is
  currently allowed (cooldown, resource cost, stun state), what a "confirm"
  button does in the current game-rule context, or any other outcome a
  pressed button causes — that decision lives in `Game.Core.*` per
  `coding-principles.md`'s Shared Core integrity rule; this skill only
  supplies the already-resolved "this input happened this frame" signal, via
  an `IInputProvider`-style abstraction Client code depends on rather than a
  concrete Input System singleton. Do not use this for the visual layout,
  Canvas hierarchy, or widget design of UI screens the Input System's
  `InputSystemUIInputModule`/on-screen controls ultimately drive — that's
  `ui-ux-programmer`'s territory; this skill only wires the input-module
  plumbing and control-path injection up to the point input reaches a UI
  event callback. Do not use this for Animator Controller/blend-tree
  authoring that visualizes movement driven by input — that's
  `unity-animation`; this skill only supplies the raw input signal an
  Animator parameter or a Shared Core movement rule consumes. Do not use this
  for NavMesh/pathfinding movement decisions — `unity-navmesh-navigation`/
  `Game.Core.*`; this skill has no opinion on where a character should go,
  only on what button/stick state the player is currently producing. Do not
  use this for XR rendering configuration or the XR Interaction Toolkit
  package (`com.unity.xr.interaction.toolkit` — grab interactables,
  teleportation, ray interactors) — this skill covers only raw XR/tracked
  device *input* (`TrackedPoseDriver`, `TrackedDevice`) as a boundary note,
  not XR rendering or interaction-toolkit authoring, and this project
  currently has no dedicated skill for that deeper XR surface.
---

# Unity Input System — Actions, Devices, PlayerInput & Rebinding

Sources: see [references/](references/) for the Manual/Scripting API root links, split by topic — [root-links.md](references/root-links.md), [architecture-and-update-loop.md](references/architecture-and-update-loop.md), [actions-bindings-and-assets.md](references/actions-bindings-and-assets.md), [interactions-and-processors.md](references/interactions-and-processors.md), [player-input-and-multiplayer.md](references/player-input-and-multiplayer.md), [rebinding.md](references/rebinding.md), [devices-and-ui-integration.md](references/devices-and-ui-integration.md), [on-screen-controls-and-xr.md](references/on-screen-controls-and-xr.md), [editor-tooling-and-debugging.md](references/editor-tooling-and-debugging.md), [migration-and-settings.md](references/migration-and-settings.md), [scripting-api.md](references/scripting-api.md).

## 1. Objective
Turn raw player input (keyboard, mouse, gamepad, touch, pen, sensors, XR controllers) into clean, decoupled, rebindable signals — the right Action/binding/composite/Interaction/Processor setup, the right consumption workflow (`PlayerInput`, generated wrapper, direct Action polling, or low-level device polling), and the right multiplayer/rebinding/UI-integration wiring — without drifting into the gameplay decisions those signals trigger, the UI layout those signals feed, the Animator work those signals drive, or XR rendering/interaction authoring beyond raw device input, all of which are sibling skills'/roles' territory.

## 2. Role
Act as the Input System specialist: given a feature that needs player input, you choose and configure the right `UnityEngine.InputSystem` Action/binding/device/component setup and expose it to Client code through a clean abstraction — you don't decide what a button press *means* for the game state (that's Shared Core's job, per Dependency Inversion in `coding-principles.md`: Client-layer code should depend on an `IInputProvider`-style abstraction, not a concrete Input System singleton, so `Game.Core.*` stays testable and swappable), and you don't reach into UI screen layout, Animator authoring, NavMesh movement decisions, or XR rendering/interaction-toolkit territory, all of which are sibling skills'/roles'.

## 3. When to invoke this skill
- Authoring or editing an `.inputactions` asset — action maps, actions, action types (`Value`/`Button`/`PassThrough`), bindings, **composite bindings** (1D Axis, 2D Vector, 3D Vector, One/Two Modifiers), **Interactions** (Press, Hold, Tap, SlowTap, MultiTap), **Processors** (Normalize, Invert, Scale, Clamp, StickDeadzone, AxisDeadzone), or Control Schemes.
- Deciding **how** Client code should consume input: the `PlayerInput` component (and which notification behavior it should use), the generated C# wrapper class, direct `InputAction.ReadValue<T>()`/`WasPressedThisFrame()` polling, or low-level `Gamepad.current`/`Keyboard.current`/`Mouse.current` polling.
- Setting up **local multiplayer**: `PlayerInputManager` join/leave behavior, device pairing, split-screen camera/viewport configuration.
- Implementing **runtime rebinding**: `InputActionRebindingExtensions.PerformInteractiveRebinding()`, applying/removing binding overrides, persisting them via `SaveBindingOverridesAsJson`/`LoadBindingOverridesFromJson`.
- Wiring up **on-screen controls** for touch platforms (`OnScreenButton`/`OnScreenStick`, or a custom `OnScreenControl`).
- Wiring the **`InputSystemUIInputModule`** onto a scene's `EventSystem` so uGUI/UI Toolkit receives Input-System-driven input instead of the legacy `StandaloneInputModule`.
- Handling **raw XR/tracked device input** (`TrackedPoseDriver`, `TrackedDevice`) as a boundary case — not the XR Interaction Toolkit package or XR rendering setup.
- Deciding the project's **Active Input Handling** setting (Old/New/Both) or migrating existing `UnityEngine.Input` calls to Actions.
- Diagnosing an input bug via the **Input Debugger** window, or setting up the **Device Simulator** for touch testing without hardware.
- Reviewing whether an existing `PlayerInput`/input-handling submission violates this project's `SendMessage`/`BroadcastMessage` ban (see Edge cases below) or leaks a subscribed action/`RebindingOperation`.
- Negative trigger: the actual gameplay decision an input signal causes (attack validity, cooldown gating, resource cost, any rule that decides an *outcome*) — that's `csharp-engineer`'s Shared Core, per `coding-principles.md`'s Shared Core integrity rule; this skill only supplies the raw "this input happened" signal.
- Negative trigger: UI screen layout/Canvas hierarchy/widget visual design the input module or on-screen controls ultimately drive — `ui-ux-programmer`; this skill stops at the `InputSystemUIInputModule`/on-screen-control plumbing.
- Negative trigger: Animator Controller/blend-tree authoring that visualizes movement driven by input — `unity-animation`; this skill only supplies the raw input value an Animator parameter or a Shared Core movement rule consumes.
- Negative trigger: NavMesh/pathfinding destination decisions — `unity-navmesh-navigation`/`Game.Core.*`; this skill has no opinion on where a character should go.
- Negative trigger: XR rendering configuration or the XR Interaction Toolkit package's grab/teleport/ray-interactor authoring — out of this skill's depth; flag it back rather than improvising, per [on-screen-controls-and-xr.md](references/on-screen-controls-and-xr.md).

## 4. How to use this skill
1. **Confirm the active input backend first.** Check `Edit → Project Settings → Player → Other Settings → Active Input Handling`, per [migration-and-settings.md](references/migration-and-settings.md). This skill's guidance targets `Input System Package (New)` (or `Both`, mid-migration); if a task is actually about the legacy `UnityEngine.Input` API with the project still on `Input Manager (Old)`, say so rather than answering with new-package API that won't run.
2. **Author Actions declaratively, not ad hoc.** Build/edit the `.inputactions` asset in the Input Actions Editor window — action maps, actions with the right `InputActionType`, bindings, composites, Interactions, Processors — per [actions-bindings-and-assets.md](references/actions-bindings-and-assets.md) and [interactions-and-processors.md](references/interactions-and-processors.md). Only drop to scripted/JSON action construction when the declarative asset genuinely can't express the need, per KISS in `coding-principles.md`.
3. **Choose the consumption workflow deliberately**, per [Workflows](references/architecture-and-update-loop.md) and [player-input-and-multiplayer.md](references/player-input-and-multiplayer.md): the generated C# wrapper class or direct `InputAction`/`InputActionReference` polling for single-player/simple cases; `PlayerInput` when its device-pairing/multiplayer machinery is actually needed; low-level `Gamepad.current`-style polling only for prototyping or a genuinely fixed single-platform scheme, never as the production default (it forfeits rebinding, composites, and deadzones).
4. **If `PlayerInput` is used, set `notificationBehavior` to `Invoke C# Events` (or `Invoke Unity Events` when Inspector wiring is genuinely useful) — never `Send Messages`/`Broadcast Messages`.** Both message-based behaviors are literally `GameObject.SendMessage`/`BroadcastMessage` under the hood, which `performance-and-algorithms.md` explicitly bans for direct dispatch. Subscribe C# events via a named method (per `coding-principles.md`'s Event handlers rule) and unsubscribe in `OnDisable()`. See [player-input-and-multiplayer.md](references/player-input-and-multiplayer.md) for the full trade-off.
5. **Wrap the Input System behind an abstraction Client code depends on**, per Dependency Inversion in `coding-principles.md`: define (or reuse) an `IInputProvider`-style interface exposing already-resolved signals (`MoveInput: Vector2`, `JumpPressedThisFrame: bool`) that a MonoBehaviour implementation backs with real `InputAction`s — `Game.Core.*` gameplay logic depends on the interface, never on `InputSystem`/`PlayerInput` directly, keeping it testable by `qa-automation-engineer` and swappable without touching Core.
6. **Cache action references; never do per-frame string lookups.** Resolve `InputAction`s once (`Awake`/`OnEnable`, or via the generated wrapper's typed properties/an `InputActionReference` field) and read them every frame from the cached reference — never call `FindAction("Name")` inside `Update()`, per `performance-and-algorithms.md`'s hot-path discipline.
7. **For multiplayer, configure `PlayerInputManager` before hand-rolling join/pairing logic**, per [player-input-and-multiplayer.md](references/player-input-and-multiplayer.md) — join behavior, device pairing, and split-screen camera/viewport assignment are all built in; start from the "Simple Multiplayer" sample's pattern rather than re-deriving it.
8. **For rebinding, use `PerformInteractiveRebinding()` with an explicit exclusion/cancel control**, dispose the `RebindingOperation` via `using` (per `coding-principles.md`'s `IDisposable` rule), and persist via `SaveBindingOverridesAsJson`/`LoadBindingOverridesFromJson` keyed per player, per [rebinding.md](references/rebinding.md).
9. **Respect the Shared Core boundary at every step.** This skill's code answers "what did the player just do" — it never answers "is that allowed right now" or "what should happen as a result." Hand that decision to `Game.Core.*` through the `IInputProvider` abstraction (or the generated wrapper's callback), per `coding-principles.md`'s Shared Core integrity rule.
10. **Hand off what's out of scope explicitly**: UI screen layout/widget design → `ui-ux-programmer`. Animator Controller/blend-tree work consuming the input signal → `unity-animation`. NavMesh/movement decisions → `unity-navmesh-navigation`/Shared Core. XR rendering/Interaction Toolkit authoring → flagged as an unowned gap, not improvised. Gameplay outcome decisions → `csharp-engineer`'s Shared Core.
11. **Validate any performance claim with a measurement** (Unity Profiler, focused on GC alloc from `InputValue.Get()`/boxed callback data or per-frame action lookups), not asserted from documentation guidance alone, per `performance-and-algorithms.md`'s Verification section.

## 5. Specific goals / tasks this skill performs
- Authoring `.inputactions` assets — action maps, actions, action types, bindings, composite bindings, Interactions, Processors, Control Schemes.
- Generating and wiring a typed C# wrapper class from an action asset, or configuring project-wide actions.
- Choosing and implementing the right consumption workflow (`PlayerInput`, generated wrapper, direct Action polling, low-level device polling) behind an `IInputProvider`-style abstraction.
- Configuring `PlayerInput`'s notification behavior correctly for this project's `SendMessage` ban.
- Setting up `PlayerInputManager` local multiplayer: joining, device pairing, split-screen.
- Implementing interactive runtime rebinding and persisting binding overrides.
- Wiring on-screen controls (`OnScreenButton`/`OnScreenStick`/custom `OnScreenControl`) for touch platforms.
- Wiring `InputSystemUIInputModule` onto a scene's `EventSystem` for uGUI/UI Toolkit input.
- Handling raw XR/tracked device input via `TrackedPoseDriver`/`TrackedDevice` (boundary case only).
- Diagnosing input issues via the Input Debugger, and setting up the Device Simulator for touch testing.
- Advising on the `Active Input Handling` project setting and legacy-to-new migration.
- Out of scope: gameplay outcome decisions triggered by input (`csharp-engineer`'s Shared Core); UI screen layout/widget design (`ui-ux-programmer`); Animator Controller/blend-tree authoring (`unity-animation`); NavMesh/movement decision logic (`unity-navmesh-navigation`/Shared Core); XR rendering/XR Interaction Toolkit authoring (unowned gap — flag, don't improvise).

## 6. Output format
```
## Input System Work — <feature/character name>
- Active Input Handling confirmed: Input System Package (New) / Both — legacy Input Manager involvement noted if any
- Consumption workflow chosen: generated C# wrapper / direct InputAction polling / PlayerInput component / low-level device polling — rationale
- Action asset touched: <name>, action map(s), action type(s) (Value/Button/PassThrough)
- Bindings/composites: <...> — Interactions/Processors applied and why
- PlayerInput behavior (if used): Invoke C# Events / Invoke Unity Events — confirmed NOT Send/Broadcast Messages, per performance-and-algorithms.md
- Multiplayer (if applicable): PlayerInputManager join behavior, device pairing, split-screen camera/viewport config
- Rebinding (if applicable): PerformInteractiveRebinding setup, override persistence mechanism, RebindingOperation disposed
- IInputProvider abstraction: <interface introduced/reused, or "not needed" + why> — confirms Client code doesn't depend on InputSystem/PlayerInput directly
- Lifecycle: Enable()/Disable()/Dispose() and event unsubscribe call sites confirmed
- Shared Core boundary: confirmed no gameplay-outcome decision made in input-layer code
- Verified on: <Profiler/manual device test, or "not yet measured">
- Hand-off: <UI layout → ui-ux-programmer / Animator → unity-animation / movement decision → unity-navmesh-navigation or Shared Core / gameplay outcome → csharp-engineer, as applicable>
- Known limitations: <...>
```

## 7. Examples
**Example 1**
- Input: "Wire up player movement and jump for a single-player controller, keeping it testable and decoupled from MonoBehaviour."
- Output: confirmed Active Input Handling = Input System Package (New); authored a `Player` action map on the project-wide actions asset with a `Move` action (`Value`/`Vector2`, 2D Vector composite bound to WASD + left stick, `StickDeadzone` processor on the gamepad binding) and a `Jump` action (`Button`, bound to Space + gamepad South button); enabled "Generate C# Class"; created `IInputProvider` (`Vector2 MoveInput { get; }`, `bool JumpPressedThisFrame { get; }`) and an `InputSystemInputProvider : MonoBehaviour, IInputProvider` that instantiates the generated wrapper in `OnEnable()`, calls `Enable()`, caches the two action references, reads them once per `Update()` into cached fields, and calls `Disable()`/`Dispose()` in `OnDisable()`; `PlayerInput` not used since single-player device pairing isn't needed. `Game.Core.PlayerMovementController` receives `IInputProvider` via constructor and decides whether a jump is actually valid (grounded, no active stun) — this skill's code never makes that call.
- Hand-off: jump validity/cooldown logic → `csharp-engineer`'s Shared Core; the resulting velocity feeding an Animator `Speed`/`IsGrounded` parameter → `unity-animation`.

**Example 2**
- Input: "Support up to 4 local co-op players joining with any gamepad, with a rebinding menu players can open mid-game."
- Output: `PlayerInputManager` configured for gamepad-only joining ("Join players when button pressed"), Split-Screen enabled with a `Camera` assigned on the `PlayerInput` prefab; `PlayerInput.notificationBehavior` set to `Invoke C# Events` (not Send Messages, per this project's ban) with `onActionTriggered` subscribed via a named method and unsubscribed in `OnDisable()`; each `PlayerInput`'s screen-space UI restricted to its own camera via `MultiplayerEventSystem` so players can't interact with each other's menus; rebinding built on `PerformInteractiveRebinding().WithControlsExcluding("Mouse").WithCancelingThrough("<Gamepad>/start")`, wrapped in `using` for disposal, with `SaveBindingOverridesAsJson()` persisted to `PlayerPrefs` keyed by `playerIndex`.
- Hand-off: the rebinding menu's actual screen layout/visual design → `ui-ux-programmer`; which score/win-condition logic reads each player's actions → `csharp-engineer`'s Shared Core.

## 8. Edge cases & guardrails
- **`PlayerInput`'s "Send Messages"/"Broadcast Messages" behaviors are literally `GameObject.SendMessage`/`BroadcastMessage`** — the exact reflection-based dispatch `performance-and-algorithms.md` bans. Default to `Invoke C# Events` (or `Invoke Unity Events` when Inspector wiring is genuinely useful) in every new `PlayerInput` setup; flag existing `Send`/`Broadcast Messages` usage in review rather than treating it as an accepted exception just because it's `PlayerInput`'s own Inspector default.
- A `Send`/`Broadcast Messages` handler's method name is derived from the action's name (`"On" + ActionName`) — **renaming an action silently breaks the handler with no compile error**, a second, independent reason to prefer `Invoke C# Events`.
- **`InputAction.CallbackContext` and `InputValue` are only valid during the callback they were passed to.** Never store either and read from it later — extract `ReadValue<T>()`/`Get<T>()` immediately inside the callback body. This is a POLA violation waiting to happen: the struct looks like ordinary data but silently returns wrong/stale results once the callback returns.
- `InputValue.Get()` (the non-generic overload) **boxes the value and allocates GC garbage** — never call it in a hot path; use the generic `Get<TValue>()` instead, per `performance-and-algorithms.md`'s no-boxing-in-hot-paths rule.
- Never call `InputAction`/`InputActionMap.FindAction("Name")` by string inside `Update()` or any per-frame method — cache the reference once, or use the generated wrapper class's typed properties, per `performance-and-algorithms.md`.
- **`PlayerInput.currentActionMap` only reflects changes made through `PlayerInput`'s own API** (`SwitchCurrentActionMap`). Calling `Enable()`/`Disable()` directly on the underlying `InputActionMap` while a `PlayerInput` owns it desyncs `PlayerInput`'s notion of the "current" map from reality — always go through `PlayerInput.SwitchCurrentActionMap(...)` once a `PlayerInput` is in the picture.
- A `RebindingOperation` implements `IDisposable` and is **not cleaned up automatically** — wrap it in `using` or explicitly `Dispose()` once the rebind completes/cancels, per `coding-principles.md`'s `IDisposable` rule.
- `LoadBindingOverridesFromJson` **clears all existing overrides by default** before applying the loaded ones — pass `false` explicitly when merging onto overrides already applied this session, or a prior in-session override silently vanishes.
- Direct device polling (`Gamepad.current`, `Keyboard.current`, `Mouse.current`) **always needs a null check** (no device connected returns `null`) and forfeits rebinding, composites, and deadzones entirely — treat it as a prototyping/fixed-scheme tool, not a production default.
- `TrackedPoseDriver.positionAction`/`rotationAction` are **Obsolete** — use `positionInput`/`rotationInput` instead, per `coding-principles.md`'s Obsolete APIs ban; never author new code against the deprecated pair even if older project code still uses them.
- **`PlayerInput` split-screen is incompatible with Cinemachine virtual cameras** (a documented Known Limitation) — surface this conflict during design, not after both systems are half-wired.
- The Input System **cannot feed IMGUI** and **cannot route text input into uGUI/TextMesh Pro** — don't promise either capability; both still need the legacy input path.
- A composite's "which side wins"/`Mode` (digital vs. analog) properties default to a specific behavior that's easy to leave unconfigured — verify diagonal-movement magnitude and simultaneous-opposite-press behavior deliberately rather than assuming the Editor default matches the design's intent.
- `OnScreenButton`/`OnScreenStick` create a virtual device matching whatever control path they target — if on-screen controls on the same screen target different device types (e.g. one references `<Gamepad>`, another `<Keyboard>`), the system silently creates multiple virtual devices; confirm that's actually intended.
- Never expand this skill's XR coverage past raw `TrackedPoseDriver`/`TrackedDevice` input — XR rendering configuration and the XR Interaction Toolkit package are a materially larger surface this project has no dedicated skill for; say so explicitly rather than improvising interaction-toolkit guidance from general Input System knowledge.
- Never claim a performance improvement (an allocation removed, a polling pattern changed) without a Profiler measurement backing it, per `performance-and-algorithms.md`'s Verification section.
- Never let input-layer code (an `IInputProvider` implementation, a `PlayerInput` callback, an on-screen control handler) decide a gameplay outcome — it supplies the "what happened" signal only; "what that means" is `Game.Core.*`'s job, per `coding-principles.md`'s Shared Core integrity rule.
