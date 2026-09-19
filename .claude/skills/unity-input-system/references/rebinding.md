# Rebinding — interactive rebinds, overrides, persistence

Sources: [User rebinding at runtime](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/user-rebinding-runtime.html), [Rebind an action at runtime](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/rebind-action-runtime.html), [Save and load rebinds](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/save-load-rebinds.html), [Display bindings](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/display-bindings.html), [Restore original bindings](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/restore-original-bindings.html), [InputActionRebindingExtensions](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/api/UnityEngine.InputSystem.InputActionRebindingExtensions.html).
Covers: SKILL.md §4 — **"Dispose the `RebindingOperation` and key saved overrides per player"**.

Letting players change their controls without editing the asset. The menu's
layout and visual design belong to `ui-ux-programmer`; what is here is the
operation, the override layer, and how it survives a restart.

## The interactive operation

| Member | Effect | Use when | Source |
|---|---|---|---|
| `PerformInteractiveRebinding()` | Starts listening and writes whichever control the player actuates onto the action's binding | Any player-facing rebind | [Rebind an action at runtime](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/rebind-action-runtime.html) |
| `WithControlsExcluding(path)` | Refuses a control as a rebind target; excluding the mouse is near-universal, since a stray movement otherwise captures itself | The rebind is for keys or buttons rather than pointer motion | [Rebind an action at runtime](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/rebind-action-runtime.html) |
| `WithCancelingThrough(path)` | Designates the control that aborts rather than completing the rebind | Always — without one the player cannot back out | [Rebind an action at runtime](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/rebind-action-runtime.html) |
| `WithExpectedControlType(type)` | Restricts what counts as a valid target, so an axis cannot be bound where a button is meant | The action's control type is narrower than what the player might press | [Rebind an action at runtime](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/rebind-action-runtime.html) |
| `WithTargetBinding(index)` and binding masks | Names which binding of a multi-binding action receives the new path | The action has both a keyboard and a gamepad binding, which is the normal case | [Rebind an action at runtime](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/rebind-action-runtime.html) |

**Critical caveat**: the operation is disposable and is not cleaned up for
you. Wrap it or dispose it explicitly when the rebind completes or cancels,
per `coding-principles.md`'s Exception handling section.

## Overrides without the interactive flow

| Member | Effect | Source |
|---|---|---|
| Apply a binding override | Sets an override path non-destructively, leaving the authored binding untouched underneath | [Restore original bindings](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/restore-original-bindings.html) |
| Remove a binding override | Restores the authored binding, which is what a reset-to-default button actually does | [Restore original bindings](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/restore-original-bindings.html) |
| Display string for a binding | Produces the human-readable control name for a UI label, so the menu does not hand-map paths to glyph names | [Display bindings](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/display-bindings.html) |

## Persistence

| Subject | What it decides | Source |
|---|---|---|
| Save overrides as JSON | Serialises only the override layer, not the whole asset, so an asset edit in a later build still reaches players who have rebound | [Save and load rebinds](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/save-load-rebinds.html) |
| Load overrides from JSON | Clears the existing overrides before applying unless told not to, which is why an override applied earlier in the session vanishes without a message | [Save and load rebinds](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/save-load-rebinds.html) |
| Storage key | One shared key means the last player to rebind overwrites everyone else — key by player index or profile in any local-multiplayer build | [Save and load rebinds](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/save-load-rebinds.html) |

The package ships a rebinding UI sample that demonstrates the full listen,
cancel and persist flow; start from it rather than re-deriving the sequence.
