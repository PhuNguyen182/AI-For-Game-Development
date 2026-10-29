# DOTween vs LitMotion

Both tweening skills exist; neither engine is the default. Which one governs a feature is a module or project decision.

## Decide, in order
1. The touched module already uses one: follow it. Mixing both in one screen or system is avoidable complexity.
2. A project-wide convention exists (Tech Spec, architecture decision, consistent pattern): follow it.
3. Neither: ask the GD or `technical-architect` before writing tween code.

## Raise it even when DOTween is not the area default
- DOTween Pro's visual Sequence editor or TMP shortcuts are needed for designer iteration without recompiling.
- The feature needs a DOTween-only capability: `DOPath` (LitMotion has none; its notes say to combine with Unity Splines) or `SetSpeedBased()`.

## Prefer LitMotion even in a DOTween area
- Hot-path or high-volume tweens where the allocation difference ([safe-mode-and-async.md](safe-mode-and-async.md)) matters, confirmed by profiling.
- Established LitMotion integration: R3/UniRx `ToObservable()`, Burst/Job path.

## Porting
`litmotion-tweening` has a DOTween to LitMotion mapping ([migration-and-rx-integration.md](../../litmotion-tweening/references/migration-and-rx-integration.md)), including what has no equivalent (`SetSpeedBased()`, `DoPath()`). No LitMotion to DOTween mapping exists: translate by hand using [shortcuts.md](shortcuts.md) and [sequences-config-control.md](sequences-config-control.md).
