---
name: litmotion-tweening
description: "LitMotion zero-allocation tweening: LMotion.Create, MotionBuilder With- options, MotionHandle, Bind/BindTo*, LSequence, Punch/Shake, awaiting, custom IMotionAdapter, LitMotionAnimation. Use for code-driven interpolation in a module on LitMotion."
user-invocable: false
---

# LitMotion

Not for: DOTween (`dotween-tweening`); reactive stream composition (`r3-reactive-extensions`); unrelated async orchestration (`unitask-async-programming`); shader/particle VFX (`vfx-particle-authoring`); force/collision movement (`unity-3d-physics`, `unity-2d-physics`); building or wiring the uGUI component being animated (`ugui`); any `Game.Core.*` code (LitMotion depends on `UnityEngine`; drive Core state from `Game.Client.*` motions).
Docs: https://annulusgames.github.io/LitMotion/articles/en/ and https://github.com/annulusgames/LitMotion — LitMotion v2 (v2.0.2); doc URLs are unversioned and track `main`, so a newer API may be missing from an installed copy.

| Reference | Read when |
|---|---|
| [getting-started.md](references/getting-started.md) | Adding LitMotion, choosing the asmdef/namespace, or checking whether a value type is built in |
| [motion-builder-and-handle.md](references/motion-builder-and-handle.md) | Creating a motion, or controlling/disposing a `MotionHandle` |
| [motion-settings.md](references/motion-settings.md) | Setting ease, loops, delay, callbacks, scheduler, or reusing settings |
| [sequence-and-vibration.md](references/sequence-and-vibration.md) | Combining motions, or building punch/shake |
| [component-bindings.md](references/component-bindings.md) | Binding to a Unity component, or writing a reusable binding |
| [text-and-tmp-animation.md](references/text-and-tmp-animation.md) | Animating a string, a numeric readout, or TMP characters |
| [async-lifecycle-and-debugging.md](references/async-lifecycle-and-debugging.md) | Awaiting completion, Edit Mode playback, exception handler, pre-sizing storage, or debugging leaks |
| [custom-adapters.md](references/custom-adapters.md) | A value type has no built-in support |
| [litmotion-animation-component.md](references/litmotion-animation-component.md) | Inspector-authored `LitMotionAnimation` or a custom animation component |
| [migration-and-rx-integration.md](references/migration-and-rx-integration.md) | Porting DOTween/LeanTween/PrimeTween/v1 code, or bridging to R3/UniRx |

## Steps
1. **Check which tween engine the module uses** — DOTween vs LitMotion is a standing per-module choice; if neither is established, `Needs-decision`, `Next: technical-architect` rather than default (see `dotween-tweening` `coexistence-and-migration.md`).
2. **Pick the `LMotion.Create` overload for the built-in value type**; no matching type means a custom adapter (step 9), never a lossy float proxy.
3. **Bind with a `BindTo*` extension before a manual `Bind` lambda.** String, numeric readout and per-character TMP use the text surface. Write a custom binding extension only once the same property is bound at 2+ call sites.
4. **Pass captured state as `Bind(state, (x, s) => ...)`**, not a capturing lambda, which allocates.
5. **Configure with the `With-` chain.** Choose `WithScheduler` for the needed cadence and `Time.timeScale` behaviour; the default `Update` follows time scale.
6. **Give every handle a disposal path** — `AddTo(target, LinkBehavior)`, `CompositeMotionHandle`, or explicit `Cancel()`/`Complete()`. A `Preserve()`d handle runs until cancelled.
7. **Use `LSequence` only for pure composition.** A mid-sequence callback, branch or side effect means procedural `async`/`await` instead (no `AppendCallback` by design).
8. **Await with the mechanism for the call site** — see the async reference. UniTask/R3/UniRx availability, Unity version or hot-path volume unstated → read `docs/tech-stack.md` and the manifest; still unknown → `Blocked` naming it: the choice spreads to every call site.
9. **Custom `IMotionAdapter`** only for an unsupported type: stateless, `RegisterGenericJobType` in the same change, `NoOptions` unless real state is needed.
10. **`LitMotion.Animation` only for Inspector-authored animation**; a programmer-authored one-off stays in code.
11. **Verify before shipping a hot-path or high-volume motion**: Burst/Collections present, `EnsureStorageCapacity` at startup, Profiler shows 0 GC alloc, and a custom adapter runs on an IL2CPP device build.

## Never
- Add a playing motion, or one with `WithLoops(-1)`, to an `LSequence` (throws).
- Leave the LitMotion Debugger enabled in a shipping build (performance cost).
- Let a motion and a Layout Group/Content Size Fitter drive the same `RectTransform` property.
- Hand-roll an `Update()` Lerp for anything beyond one trivial value.

## Output
```
## LitMotion Work — <feature>
- Overload / adapter: <LMotion.Create overload, String.CreateNNBytes, or custom adapter>
- Binding: <BindTo* used, or Bind(state, action)>
- Configuration: <ease, loops, delay, scheduler, callbacks>
- Composition: <LSequence, or async/await>
- Completion: <await / ToUniTask / ToYieldInstruction / ToDisposable / ToObservable>
- Disposal: <AddTo + LinkBehavior / CompositeMotionHandle / explicit>
- Verification: <Profiler alloc check result, or "not yet run">
- Known limitations: <...>
```
On request only, add `Latent concerns` and `Future remediation`, each with its trigger.

## Example
- "Just Lerp it in `Update()`" -> declined: re-implements easing, loops, delay and disposal; used `LMotion.Create(...).WithEase(...).BindTo...()`.
