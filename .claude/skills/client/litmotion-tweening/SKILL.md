---
name: litmotion-tweening
description: >
  LitMotion — zero-allocation, DOTS-optimized Unity tweening: `LMotion.Create()`,
  `MotionBuilder<TValue,TOptions,TAdapter>`, `MotionHandle`
  (`Complete`/`Cancel`/`TryComplete`/`AddTo`/`Preserve`/`PlaybackSpeed`/`Time`),
  `With-` chain methods (`WithEase`, `WithLoops`, `WithDelay`, `WithScheduler`,
  `WithOnComplete`), `Bind`/`BindTo*` extensions (Transform, RectTransform,
  uGUI, TextMeshPro, SpriteRenderer, Material, Camera, Rigidbody), `LSequence`
  composition, `LMotion.Punch`/`LMotion.Shake`, custom
  `IMotionAdapter`/`IMotionOptions`, and the Inspector-driven
  `LitMotion.Animation` package.
  Use for any code- or Inspector-authored interpolation of a value over time.
  Not for: general reactive streams (`r3-reactive-extensions`), plain async
  orchestration (`unitask-async-programming`), shader/particle VFX
  (`vfx-particle-authoring`), physics-driven movement (`unity-3d-physics`).
---

# LitMotion — Zero-Allocation Tweening for Unity

## Bundled resources

### References
Read-only context, loaded on demand so this file stays short.

| File | Contents | Read when |
|---|---|---|
| [root-links.md](references/root-links.md) | Every upstream LitMotion doc/API/source page this skill was built from | Looking for a page no other reference covers |
| [getting-started.md](references/getting-started.md) | Requirements, install methods, package/namespace layout, supported value types, quick-start shape | Adding LitMotion to a project, or deciding which package/asmdef to reference |
| [motion-builder-and-handle.md](references/motion-builder-and-handle.md) | `LMotion.Create` overloads, `Bind`/`RunWithoutBinding`, closure-avoidance, `MotionHandle` control/lifecycle members | Creating any motion, or controlling/disposing an existing `MotionHandle` |
| [motion-settings.md](references/motion-settings.md) | Every `With-` configuration method, `MotionScheduler` timing table, `MotionSettings<T,TOptions>`/`SerializableMotionSettings` | Configuring easing, looping, delay, callbacks, or update timing |
| [sequence-and-vibration.md](references/sequence-and-vibration.md) | `LSequence` (`Append`/`Join`/`Insert`/`AppendInterval`/`Run`), `LMotion.Punch`/`LMotion.Shake` | Combining several motions, or building a punch/shake effect |
| [component-bindings.md](references/component-bindings.md) | `LitMotion.Extensions` `BindTo*` catalogue by component category, the custom-binding-extension-method pattern | Binding to a Unity component, or writing a reusable binding for one |
| [text-and-tmp-animation.md](references/text-and-tmp-animation.md) | `LMotion.String.Create*Bytes`, numeric `BindToText` formatting, TextMesh Pro per-character animation, ZString integration | Animating a string, a numeric readout, or individual TMP characters |
| [async-lifecycle-and-debugging.md](references/async-lifecycle-and-debugging.md) | Awaiting a handle (`GetAwaiter`/`ToUniTask`/`ToValueTask`/`ToAwaitable`/`ToYieldInstruction`), `ToDisposable`, exception handling, `ManualMotionDispatcher`, Editor playback, `EnsureStorageCapacity`, LitMotion Debugger | Waiting on motion completion, running motions in Edit Mode, or diagnosing leaks/allocations |
| [custom-adapters.md](references/custom-adapters.md) | `IMotionAdapter<T,TOptions>`, `IMotionOptions`, `RegisterGenericJobType`, adapter authoring steps | A value type has no built-in support |
| [litmotion-animation-component.md](references/litmotion-animation-component.md) | `LitMotionAnimation` component, Animation Components, C# control (`Play`/`Pause`/`Stop`/`Restart`), `LitMotionAnimationComponent`/`PropertyAnimationComponent<TObject,TValue,TOptions,TAdapter>` | Building or extending an Inspector-authored animation |
| [migration-and-rx-integration.md](references/migration-and-rx-integration.md) | `ToObservable`/`BindToReactiveProperty` for R3/UniRx, DOTween/LeanTween/PrimeTween/v1 migration cheat sheets, FAQ design decisions | Porting existing tween code, or bridging a motion into a reactive pipeline |

## 1. Objective
Animate values — Transform, UI, material, text, camera, physics, or a custom type — through LitMotion's struct-based `MotionBuilder`/`MotionHandle` API with genuinely zero per-frame and per-motion-creation allocation, correct disposal/cancellation discipline, and the configuration (easing, looping, scheduler timing) the Tech Spec actually calls for — without silently reintroducing a closure allocation, leaking an un-disposed handle, or reaching for a heavier mechanism (Sequence, a custom adapter, Rx) than the task needs.

## 2. Role
Act as the tweening/animation specialist for the client track — the tool Unity Engineer, UI/UX Programmer, and Technical Artist reach for whenever a feature needs a code-driven or Inspector-driven interpolation of a value over time: a UI transition, a transform move, a camera shake, a material fade, a text reveal, or a punch/shake feedback effect.

## 3. When to invoke this skill
- Animating a built-in or custom value (Transform position/rotation/scale, UI color/alpha/size, material property, camera field, Rigidbody move, TMP character) via `LMotion.Create()`.
- Combining several motions into one controllable unit with `LSequence`, or building a punch/shake feedback effect.
- Waiting on a motion's completion from a coroutine, `async`/`await` method, or as an `IDisposable`/`IObservable<T>`.
- Building or extending an Inspector-authored animation with the `LitMotion.Animation` package, including a custom `LitMotionAnimationComponent`.
- A value type has no built-in adapter and needs a custom `IMotionAdapter<T,TOptions>`.
- Porting existing DOTween/LeanTween/PrimeTween/LitMotion-v1 tween code to current LitMotion.
- Negative trigger: composing a general reactive event/state stream unrelated to a timed interpolation — that's `r3-reactive-extensions`; LitMotion only produces the `Observable<T>`, it doesn't own stream composition.
- Negative trigger: orchestrating unrelated async game logic with no motion involved — that's `unitask-async-programming`.
- Negative trigger: a shader-driven or particle-system visual effect — that's `vfx-particle-authoring`/`technical-artist`; LitMotion animates discrete properties, not GPU-simulated effects.
- Negative trigger: physically simulated movement driven by forces/collisions rather than a fixed-duration interpolation — that's `unity-3d-physics`/`unity-2d-physics`.
- Negative trigger: any `Game.Core.*` code — LitMotion's core package depends on `UnityEngine` (Vector3, Color, MonoBehaviour scheduling), which `coding-principles.md`'s Shared Core integrity section forbids in Core. Drive Core state changes from `Game.Client.*` motions instead.

## 4. How to use this skill
1. **Pick the `LMotion.Create` overload matching the value's built-in type** (int/long/float/double/Vector2/Vector3/Vector4/Quaternion/Color/Rect), per [getting-started.md](references/getting-started.md) — escalate to a custom adapter (step 8) only once the type is genuinely unsupported, never by routing an unsupported type through a lossy float proxy.
2. **Bind with a built-in `LitMotion.Extensions` `BindTo*` method before writing a manual `Bind()` lambda**, per [component-bindings.md](references/component-bindings.md) — the axis-decomposed family (`BindToPosition`/`BindToPositionX`/`BindToPositionXY`, etc.) already covers Transform, RectTransform, uGUI, TextMeshPro, SpriteRenderer, Material, Camera, Rigidbody. For a string, a numeric readout, or per-character TMP animation, use the dedicated `LMotion.String`/`BindToText`/`BindToTMPChar*` surface in [text-and-tmp-animation.md](references/text-and-tmp-animation.md) instead. Write a custom binding extension method only once the same property is bound at more than one call site — a single-use extension is speculative complexity YAGNI forbids.
3. **Pass captured state into `Bind(TState, Action<TValue,TState>)` instead of a capturing lambda** whenever the callback references an object already available by reference, per [motion-builder-and-handle.md](references/motion-builder-and-handle.md) — the motion struct itself allocates nothing, but a closure inside `Bind()` still does, which is exactly the per-frame/per-call allocation `performance-and-algorithms.md`'s Memory discipline section forbids.
4. **Configure via the `With-` chain rather than re-deriving the same behavior by hand**, per [motion-settings.md](references/motion-settings.md) — choose `WithScheduler` deliberately by the required update cadence and whether `Time.timeScale`/pause should apply; leaving it default silently ties the motion to `Update()` with time-scale applied even when the feature needs otherwise.
5. **Give every `MotionHandle` an explicit disposal path** — `AddTo(GameObject/Component, LinkBehavior)` for a component-scoped motion, `CompositeMotionHandle` for several owned together, or an explicit `Cancel()`/`Complete()`. Never leave a `Preserve()`d handle unmanaged, per [motion-builder-and-handle.md](references/motion-builder-and-handle.md) — it is designed to keep running until `Cancel()` is called explicitly.
6. **Reach for `LSequence` only for structural composition** (`Append`/`Join`/`Insert`/`AppendInterval`), per [sequence-and-vibration.md](references/sequence-and-vibration.md). Once the animation needs a mid-sequence callback, branching, or per-step side effects, switch to procedural `async`/`await` chaining instead — `LSequence` intentionally has no `AppendCallback`, by the same design reasoning as the FAQ's `DelayedCall` answer in [migration-and-rx-integration.md](references/migration-and-rx-integration.md).
7. **Await completion with the mechanism matching the call site**, per [async-lifecycle-and-debugging.md](references/async-lifecycle-and-debugging.md) — `await handle` or `ToUniTask()` inside an `async` method (preferred once UniTask is installed), `ToYieldInstruction()` only inside a legacy coroutine, `ToValueTask()`/`ToAwaitable()` only when UniTask is unavailable.
8. **Write a custom `IMotionAdapter<TValue,TOptions>` only for a genuinely unsupported value type**, per [custom-adapters.md](references/custom-adapters.md) — keep the adapter stateless, register `RegisterGenericJobType<MotionUpdateJob<TValue,TOptions,TAdapter>>` for Burst, and use `NoOptions` unless the motion needs real extra state.
9. **Reach for the `LitMotion.Animation` package only when the animation is meant to be authored/iterated in the Inspector**, per [litmotion-animation-component.md](references/litmotion-animation-component.md) — a one-off, programmer-authored tween stays in code via `LMotion.Create`; reserve Inspector-built `LitMotionAnimation` components for designer/artist iteration without a recompile.
10. **Verify the zero-allocation and Burst claims with the Profiler before shipping a hot-path or high-volume motion**, per `performance-and-algorithms.md`'s Verification section — confirm Burst 1.6.0+/Collections 1.5.1+/Mathematics are present (per [getting-started.md](references/getting-started.md)) and call `MotionDispatcher.EnsureStorageCapacity()` at startup for any value/options/adapter combination expected at high volume, per [async-lifecycle-and-debugging.md](references/async-lifecycle-and-debugging.md).
11. **If the async ecosystem (UniTask/R3/UniRx availability), target Unity/C# version, or hot-path volume is unstated, ask before committing to an async mechanism or a scripting define** — per [migration-and-rx-integration.md](references/migration-and-rx-integration.md), UniTask vs. `ValueTask` and R3 vs. UniRx are project-wide ecosystem choices that ripple through every call site once picked, and are not recoverable from the code alone afterward.

## 5. Specific goals / tasks this skill performs
- Creating, configuring, and binding a motion for a built-in or component-specific value via `LMotion.Create()` and `BindTo*`.
- Composing motions into a `LSequence`, or building a `Punch`/`Shake` vibration effect.
- Choosing and wiring the correct completion-waiting mechanism (`await`, `ToUniTask`, `ToYieldInstruction`, `ToDisposable`, `ToObservable`).
- Authoring a custom `IMotionAdapter`/`IMotionOptions` for an unsupported type, or a custom `LitMotionAnimationComponent`/`PropertyAnimationComponent<T>` for the Inspector-driven package.
- Auditing `MotionHandle` disposal, closure allocation in `Bind()`, and scheduler/timing choices in existing code.
- Porting DOTween/LeanTween/PrimeTween/LitMotion-v1 tween code to current LitMotion idioms.
- Out of scope: general reactive stream composition (`r3-reactive-extensions`), unrelated async orchestration (`unitask-async-programming`), shader/particle VFX (`vfx-particle-authoring`), physics-driven movement (`unity-3d-physics`/`unity-2d-physics`), any `Game.Core.*` usage.

## 6. Output format
```
## LitMotion Work — <animation/feature name>
- Value type & overload: <built-in LMotion.Create overload, LMotion.String.CreateNNBytes, or custom IMotionAdapter> — why
- Binding: <BindTo* extension used, or Bind(state, action) with closure avoidance noted>
- Configuration: <Ease/Loops+LoopType/Delay+DelayType/Scheduler/callbacks set, and why each was chosen>
- Composition: <LSequence Append/Join/Insert, or procedural async/await> — rationale
- Completion handling: <await/ToUniTask/ToYieldInstruction/ToDisposable/ToObservable> — matches call site
- Disposal: <AddTo(target, LinkBehavior) / CompositeMotionHandle / explicit Cancel-Complete> — owner
- Custom extension: <IMotionAdapter / LitMotionAnimationComponent / binding extension method, or "not needed">
- Verification: <Profiler allocation check confirmed, or "not yet run">
- Layer: Game.Client.* — never Game.Core.*
- Known limitations: <...>
```

**Extended report — emit ONLY when the requester asks for it.** It replaces the one-line `Known limitations` above with all three fields:
```
- Known limitations: <what this animation/integration does not cover>
- Latent concerns: <assumptions holding only under current volume/scheduler/ecosystem choices>
- Future remediation: <the concrete fix for each, and its trigger condition>
```

## 7. Examples
**Example 1**
- Input: a settings panel needs to fade in and slide up from below when opened, then be dismissable by the player.
- Output: `LMotion.Create(startAlpha, 1f, 0.3f).WithEase(Ease.OutQuad).BindToAlpha(canvasGroup)` and a second motion via `BindToAnchoredPositionY` on the `RectTransform`, both `AddTo(gameObject, LinkBehavior.CancelOnDisable)` so reopening the panel doesn't stack handles from a prior close.

**Example 2**
- Input: "just Lerp the value manually inside `Update()`, it's simpler than pulling in a tweening call."
- Output: declined for anything beyond a single trivial case — a hand-rolled `Update()` Lerp re-implements easing, looping, delay, and disposal that `LMotion.Create` already gives for free with zero allocation, and scales badly once a second property needs the same treatment; used `LMotion.Create(...).WithEase(...).BindTo...()` instead, per [motion-builder-and-handle.md](references/motion-builder-and-handle.md).

**Example 3**
- Input: an inventory system needs to animate a project-specific `GridCoordinate` struct (two ints) that has no built-in adapter.
- Output: implemented `IMotionAdapter<GridCoordinate, NoOptions>` with `Evaluate()` doing per-field integer interpolation, added `[assembly: RegisterGenericJobType(typeof(MotionUpdateJob<GridCoordinate, NoOptions, GridCoordinateMotionAdapter>))]`, and created motions via `LMotion.Create<GridCoordinate, NoOptions, GridCoordinateMotionAdapter>(...)`, per [custom-adapters.md](references/custom-adapters.md).

**Example 4**
- Input: a boss intro needs three transform motions in sequence, then a callback, then a UI element to fade in.
- Output: declined building it as one `LSequence` with a callback bolted on — `LSequence` has no `AppendCallback` by design. Wrote it as procedural `async`/`await`: `await` each `LMotion.Create(...)` in order, ran the mid-animation logic between awaits, then `await`ed the UI fade motion — per step 6 and [migration-and-rx-integration.md](references/migration-and-rx-integration.md)'s FAQ notes.

## 8. Edge cases & guardrails
- Never leave a `Preserve()`d `MotionHandle` without an explicit `Cancel()`/`AddTo()` — it is designed to outlive normal completion and will run indefinitely otherwise.
- Never pass a capturing lambda to `Bind()` where the referenced state is already available as an object — use `Bind(state, (x, state) => ...)` instead, per step 3.
- Never add a motion that is already playing, or one with an infinite loop (`WithLoops(-1)`), into a `LSequence` — it throws.
- Never place `LitMotion`/`LitMotion.Extensions` types in `Game.Core.*` — the package depends on `UnityEngine`; drive Core state changes from `Game.Client.*` instead.
- Never leave the LitMotion Debugger enabled in a shipping build — per [async-lifecycle-and-debugging.md](references/async-lifecycle-and-debugging.md), it has a real, documented performance cost.
- Never write a custom `IMotionAdapter` for a type that already has one — check [getting-started.md](references/getting-started.md)'s supported-types list first.
- If the project's UniTask/R3/UniRx availability or hot-path volume is unstated, ask per step 11 — the async mechanism and scripting-define choice are not recoverable from the code afterward.
