# Interactive Rebinding & Persisting Overrides

[Manual — User rebinding at runtime](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/user-rebinding-runtime.html) · [Rebind an action at runtime](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/rebind-action-runtime.html) · [Save and load rebinds](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/save-load-rebinds.html) · [Look up bindings](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/look-up-bindings.html) · [Display bindings](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/display-bindings.html) · [Restore original bindings](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/restore-original-bindings.html) · [API — InputActionRebindingExtensions](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/api/UnityEngine.InputSystem.InputActionRebindingExtensions.html)

## Interactive rebinding — `PerformInteractiveRebinding`

```csharp
RebindingOperation rebindOperation = actionToRebind
    .PerformInteractiveRebinding()
    .Start();
```

`InputAction.PerformInteractiveRebinding()` (an extension method on `InputActionRebindingExtensions`) starts listening for input from any Device matching the action's expected control type; whichever control the player actuates gets written as the action's new binding path. It returns a `RebindingOperation`, configured fluently before `.Start()`:

| Method | Purpose |
|---|---|
| `WithExpectedControlType(string)` | Restrict which control type counts as a valid rebind target (e.g. only buttons). |
| `WithControlsExcluding(string)` | Exclude a control path/device from being accepted (commonly used to exclude `Mouse` so an accidental mouse move doesn't get captured as a rebind). |
| `WithCancelingThrough(string)` | Designate a control (typically `Escape`) that aborts the rebind instead of completing it. |
| `WithTargetBinding(int)` / `WithBindingGroup(string)` / `WithBindingMask(...)` | Specify exactly which binding on the action receives the new path — required once an action has more than one binding (e.g. keyboard + gamepad). |

When multiple controls are actuated at once during a rebind, the system picks the one with the highest magnitude — relevant when a player rests a hand on a stick while trying to rebind a keyboard key.

**Lifecycle**: `RebindingOperation` implements `IDisposable` and is **not automatically cleaned up** — per `coding-principles.md`'s Exception handling rule ("use `using` for any `IDisposable`"), wrap it in a `using` statement/declaration or explicitly call `Dispose()` once the rebind completes or is canceled, rather than letting it leak.

Unity ships a full "Rebinding UI" sample (Package Manager → Input System → Samples) — start from its pattern for an actual rebind menu rather than re-deriving the interactive-rebind/cancel/timeout flow from scratch.

## Applying/removing overrides without the interactive flow

`InputActionRebindingExtensions.ApplyBindingOverride(...)` sets a binding's `overridePath` (and optionally `overrideProcessors`/`overrideInteractions`) directly from code, non-destructively — the original binding data is untouched, only the override layer changes. `RemoveBindingOverride(...)` clears it back to the original. Useful for a "reset to gamepad default" button, or applying a scripted remap without going through the interactive UI at all.

## Persisting rebinds — `SaveBindingOverridesAsJson` / `LoadBindingOverridesFromJson`

```csharp
// Save
string rebinds = playerInput.actions.SaveBindingOverridesAsJson();
PlayerPrefs.SetString("rebinds", rebinds);

// Load
string rebinds = PlayerPrefs.GetString("rebinds");
playerInput.actions.LoadBindingOverridesFromJson(rebinds);
```

**Gotcha**: `LoadBindingOverridesFromJson` **clears all existing overrides on the action asset before applying the loaded ones**, by default — pass `false` as the second argument if that clearing behavior isn't wanted (e.g. merging saved overrides on top of overrides already applied programmatically this session). Missing this default is a common source of "my earlier override silently disappeared" bugs.

For per-player persistence in local multiplayer, key the saved JSON string by `playerIndex` (or a stable player-profile ID) rather than one shared key — otherwise the last player to rebind overwrites everyone else's saved preferences.
