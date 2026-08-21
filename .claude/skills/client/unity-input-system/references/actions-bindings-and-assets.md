# Actions, Bindings and Assets — action types, composites, Control Schemes

Sources: [Actions](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/Actions.html), [Input action assets](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/action-assets.html), [Action type reference](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/action-type-reference.html), [Bindings](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/bindings.html), [Composite bindings](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/composite-bindings.html), [Control schemes](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/control-schemes.html), [Project-wide actions](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/about-project-wide-actions.html), [Generate C# API from actions](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/generate-cs-api-from-actions.html).
Covers: SKILL.md §4 — **"Author actions in the `.inputactions` asset rather than in code"**, **"Pick the action type from what the control produces"**, **"Express multi-control input as a composite binding rather than several actions"**.

The authoring surface: what an asset holds, what each action type does to the
value and its phases, and how several controls become one signal. Timing
patterns and value transforms are next door in
[interactions-and-processors.md](interactions-and-processors.md).

## The asset

| Subject | What it decides | Source |
|---|---|---|
| `.inputactions` asset | Holds action maps, actions, bindings and Control Schemes together; it is what the editor, the generated wrapper, the rebinding API and the Debugger all read, so authoring anywhere else fragments the source of truth | [Input action assets](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/action-assets.html) |
| Project-wide actions | One designated asset preloaded at startup, kept alive, and enabled by default, reachable through the static hub without a serialized reference — a manually created asset gets none of that and must be enabled by the code that owns it | [Project-wide actions](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/about-project-wide-actions.html) |
| Action map | The enable and disable unit, which is what makes a Player map and a UI map swappable as a pair when a menu opens | [Actions](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/Actions.html) |
| Generated C# class | A typed property per map and action, so a rename becomes a compile error instead of a runtime lookup that silently finds nothing | [Generate C# API from actions](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/generate-cs-api-from-actions.html) |
| Scripted or JSON construction | Building actions and bindings from code, for the rare case where the set genuinely is not known until runtime; it forfeits the editor and the generated wrapper | [Actions](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/Actions.html) |

**Critical caveat**: an action that is never enabled produces its default
value forever and raises nothing. Enabling is per map or per action, and a
non project-wide asset starts disabled.

## Action types

| Type | Phase and value behaviour | Use for | Source |
|---|---|---|---|
| `Button` | Performs once when actuation crosses the press point; resolves competing controls to the most actuated | Discrete intents — jump, fire, interact | [Action type reference](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/action-type-reference.html) |
| `Value` | Performs continuously while actuated, with the same conflict resolution — a discrete intent authored here fires every frame it is held | Analog and continuous input — movement, look, triggers | [Action type reference](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/action-type-reference.html) |
| `PassThrough` | No phase semantics and no conflict resolution; every bound control reports independently | Aggregating several sources that should all count, rather than picking one current value | [Action type reference](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/action-type-reference.html) |

## Bindings and composites

| Binding | Parts | Produces | Source |
|---|---|---|---|
| Plain binding | One control path such as a device layout plus a control name | The control's own value | [Bindings](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/bindings.html) |
| 1D Axis | Positive and negative buttons | A float; its tie-breaking property decides what happens when both are held, and leaving it unset makes opposing keys behave arbitrarily | [Composite bindings](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/composite-bindings.html) |
| 2D Vector | Four buttons | A `Vector2`; its mode decides whether a diagonal is normalised, which is why an unset mode makes keyboard diagonals faster than a stick | [Composite bindings](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/composite-bindings.html) |
| 3D Vector | Six buttons | A `Vector3`, with the same normalisation question as the 2D form | [Composite bindings](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/composite-bindings.html) |
| One Modifier | A modifier plus a binding | The bound control's value, only while the modifier is held — the chord mechanism | [Composite bindings](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/composite-bindings.html) |
| Two Modifiers | Two modifiers plus a binding | The same, for a two-key chord | [Composite bindings](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/composite-bindings.html) |

## Control Schemes

| Subject | What it decides | Source |
|---|---|---|
| Device requirements | A scheme with an empty requirement list matches nothing and does nothing, which reads as bindings being ignored | [Control schemes](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/control-schemes.html) |
| Binding groups | Which bindings belong to which scheme, so one action carries both a keyboard and a gamepad path without a device check in gameplay code | [Control schemes](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/control-schemes.html) |
| `InputActionReference` | A serialized reference to one action inside an asset, so an Inspector field replaces a string lookup at the call site | [InputActionReference](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/api/UnityEngine.InputSystem.InputActionReference.html) |
