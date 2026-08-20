# Actions, Bindings, Composites & Action Assets

[Manual — Actions](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/Actions.html) · [Manual — Input action assets](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/action-assets.html) · [Manual — Action and control types](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/action-and-control-types.html) · [Manual — Bindings](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/bindings.html) · [Manual — Composite bindings](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/composite-bindings.html) · [Manual — Control schemes](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/control-schemes.html) · [Manual — About project-wide actions](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/about-project-wide-actions.html) · [Manual — Generate C# API from actions](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/generate-cs-api-from-actions.html)

## Action Assets — the authored source of truth

An `.inputactions` file (backed by `InputActionAsset`) holds one or more `InputActionMap`s, each holding `InputAction`s with their `InputBinding`s, plus the asset's `InputControlScheme`s. Author it in the **Input Actions Editor** window (see [editor-tooling-and-debugging.md](editor-tooling-and-debugging.md)), not by hand-editing the underlying JSON, unless a task specifically calls for scripted/JSON-driven configuration (see "Configure input from code/JSON" further below).

**Project-wide actions** ([about-project-wide-actions.html](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/about-project-wide-actions.html)): one designated `InputActionAsset` can be assigned as the project's default — it's preloaded at startup, kept alive for the app's lifetime, and enabled by default. Reach it anywhere via `InputSystem.actions.FindAction("Move")` without holding a manual reference. Unity's own guidance: use a single project-wide asset unless the project genuinely needs more than one — don't split into multiple assets speculatively (YAGNI, per `coding-principles.md`).

**Generated C# wrapper class** ([generate-cs-api-from-actions.html](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/generate-cs-api-from-actions.html)): enabling "Generate C# Class" on the asset's Inspector produces a typed class exposing every action map/action as a property — no more string-keyed `FindAction()` lookups. Typical lifecycle: instantiate in `OnEnable()`, call `SetCallbacks(this)` to register a MonoBehaviour implementing the generated per-map interface (e.g. `IPlayerActions`), `Enable()`/`Disable()` paired with the MonoBehaviour's own `OnEnable()`/`OnDisable()`, and implement `OnMove(InputAction.CallbackContext)`-style methods. **Prefer this over raw string-keyed `FindAction()` calls in this project** — it's compile-time safe and avoids a hidden string-lookup cost if called repeatedly, consistent with `naming-convention.md`'s "no magic strings" spirit and `performance-and-algorithms.md`'s hot-path discipline.

## Action Types — `InputActionType`

[Manual — Action types reference](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/action-type-reference.html):

| Type | Behavior | Use for |
|---|---|---|
| `Value` | Continuously-changing input (stick, mouse delta, orientation); provides phase info and **conflict resolution** — when multiple bound controls are actuated, the most-actuated one drives the action. | Movement axes, look input, anything analog. |
| `Button` | Discrete on/off controls; provides phase info and conflict resolution. | Jump, fire, interact — anything binary. |
| `PassThrough` | Same control shapes as `Value`, but **no phase info and no conflict resolution** — every bound control's change is reported independently rather than picking one "winner." | Aggregating input from several controls that should all matter simultaneously (e.g. summing multiple analog sources), not for a single canonical "current value." |

## Bindings & Composite Bindings

A normal `InputBinding` targets one control path (`<Gamepad>/buttonSouth`). A **composite binding** synthesizes one value out of several **part bindings**, per [composite-bindings.html](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/composite-bindings.html):

| Composite | Part bindings | Output | Notes |
|---|---|---|---|
| **1D Axis** (Positive/Negative) | `positive`, `negative` (buttons) | `float` | Pulls the axis toward −1/+1. Has a **"which side wins"** property when both are pressed simultaneously — set it deliberately (last pressed wins by default in most templates; verify per-project rather than assuming). |
| **2D Vector** (Up/Down/Left/Right) | four buttons | `Vector2` | The standard WASD/D-pad composite. Has a `Mode` property (Digital/Digital Normalized/Analog) controlling whether diagonal magnitude is normalized — leaving this unconfigured silently changes diagonal move speed on keyboard vs. stick. |
| **3D Vector** (Up/Down/Left/Right/Forward/Backward) | six buttons | `Vector3` | Same digital/analog `Mode` concern as 2D Vector, one axis pair added. |
| **One Modifier** | `modifier`, `binding` | Same type as the bound control | "Hold SHIFT + 1" style chords. |
| **Two Modifiers** | `modifier1`, `modifier2`, `binding` | Same type as the bound control | "Hold SHIFT+CTRL + 1" style chords. |

This is the mechanism behind a WASD/stick-driven `Move` action — one 2D Vector composite, not four separate actions manually summed in script.

## Control Schemes

[Manual — Control schemes](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/control-schemes.html): a named set of device requirements (e.g. "Gamepad", "Keyboard&Mouse") that groups which bindings apply for which device type. A new scheme starts with an empty device-type list — it must have at least one device requirement before it does anything. Group bindings under the scheme they belong to in the Input Actions Editor so the same action can have a gamepad binding and a keyboard/mouse binding active only for the matching device, without runtime `if` branching on device type in game code.

## Scripting an action asset directly (when authoring in the window isn't the right tool)

For editor tooling, SDK/config code, or one-off Shared-Core-adjacent setup where a hand-authored `.inputactions` asset is overkill, the API supports building actions/bindings purely from code (`new InputAction(...)`, `InputActionSetupExtensions.AddBinding(...)`) or from a raw JSON string (`InputActionAsset.FromJson`/`.LoadFromJson`). Reach for this only when the declarative asset genuinely can't express the need (per KISS in `coding-principles.md`) — the Input Actions Editor is the default authoring path for anything a designer/engineer will tune more than once.

## Related scripting types

`InputActionReference` — a serializable reference to one specific `InputAction` inside an `InputActionAsset`, usable as an Inspector-exposed field (`[SerializeField] private InputActionReference jumpActionReference;`, per `naming-convention.md`'s Unity override for serialized fields) instead of a hard-coded string lookup. See [scripting-api.md](scripting-api.md) for the full class list (`InputAction`, `InputActionMap`, `InputActionAsset`, `InputBinding`, `InputBindingComposite`).
