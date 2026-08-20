# Animator Override Controller

Sources: `https://docs.unity3d.com/Manual/AnimatorOverrideController.html`, `https://docs.unity3d.com/ScriptReference/AnimatorOverrideController.html`, and sub-pages (see [root-links.md](root-links.md)).

## Purpose
An `AnimatorOverrideController` asset lets you override which `AnimationClip`s an Animator Controller plays "while retaining the structure, parameters, and logic of its state machine." It exists to avoid duplicating an entire Animator Controller graph just to swap the clips it plays.

Canonical use case: multiple character variants (e.g. goblin, ogre, elf) that share identical state-machine logic (same states, transitions, parameters) but need different animation clips per variant. Build **one** base Animator Controller (see [animator-controller.md](animator-controller.md)), then create one Animator Override Controller per variant that only remaps clips.

## Authoring workflow (Editor)
1. **Assets > Create > Animation > Animator Override Controller**.
2. Assign the base Animator Controller via the new asset's `Controller` field.
3. The Inspector shows a two-column table (original clip → override clip); pick a replacement clip for each entry you want to override; leave others unset to keep the base clip.
4. Assign the Animator Override Controller (instead of the base Animator Controller) to the target GameObject's `Animator` component — or set it via script at runtime (see API below).

**Gotcha:** transition **Exit Time** should be authored in *normalized* time, not `Fixed Duration`/seconds, when the controller will be used with override clips of different lengths — an override clip shorter than a seconds-based exit time can cause that transition to be skipped/ignored entirely.

## Scripting API (`UnityEngine.AnimatorOverrideController`)

| Member | Signature | Description |
|---|---|---|
| Constructor | `AnimatorOverrideController(RuntimeAnimatorController controller)` | Creates an override controller wrapping the given base controller. |
| Indexer | `this[string name]` | Get/set the override for the original clip named `name` — returns the override clip if set, otherwise the original clip. |
| `ApplyOverrides` | `ApplyOverrides(List<KeyValuePair<AnimationClip, AnimationClip>> overrides)` | Applies a batch of clip overrides in one call. **Preferred over the indexer for multiple changes** — each individual indexer assignment triggers a clip-binding reallocation, so batching via `ApplyOverrides` avoids repeated reallocation cost when changing several clips at once. |
| `GetOverrides` | `GetOverrides(List<KeyValuePair<AnimationClip, AnimationClip>> overrides)` | Fills the passed list with the currently defined `(original, override)` clip pairs. |
| `runtimeAnimatorController` | property | The base `RuntimeAnimatorController` this override controller wraps. |
| `overridesCount` | property | Number of overrides currently defined. |
| `animationClips` | property (inherited from `RuntimeAnimatorController`) | All `AnimationClip`s used by the (overridden) controller. |

To apply at runtime, assign the `AnimatorOverrideController` instance to `Animator.runtimeAnimatorController` (see [animator-component.md](animator-component.md)) — the Animator will then play clips through the override mapping while running the base controller's state machine/transition/parameter logic unchanged.

```csharp
AnimatorOverrideController overrideController = new(baseController);
List<KeyValuePair<AnimationClip, AnimationClip>> overrides = new();
overrideController.GetOverrides(overrides);
// Replace entries in `overrides` as needed, then:
overrideController.ApplyOverrides(overrides);
this._animator.runtimeAnimatorController = overrideController;
```

## Practical guidance
- Use an Animator Override Controller whenever multiple visual variants (skins, weapon sets, character races) need to share one state machine — this is the direct SOLID/KISS answer to "don't duplicate the whole controller per variant" (Open/Closed: extend by adding a new override asset, not by editing/branching the base controller).
- Batch multiple clip swaps through `ApplyOverrides` rather than repeated indexer (`this[name] = clip`) assignments in the same frame — each indexer write causes its own clip-binding reallocation; per this project's performance rules, avoid that avoidable per-call cost when changing several clips together (verify with the Profiler if this is on a hot path).
- Author transitions with `Has Exit Time`/durations in normalized time (not `Fixed Duration` seconds) whenever a controller is designed to be reused via override controllers with clips of varying length — otherwise a shorter override clip can silently skip a transition.
- Keep override-controller assignment itself in `Game.Client.*` (it's a Unity-only API); if which variant to use is determined by gameplay state (e.g. equipped weapon type from Shared Core inventory data), read that decision from `Game.Core.*` and only perform the `runtimeAnimatorController` assignment in the Client layer, per `coding-principles.md`'s Shared Core integrity rule.
