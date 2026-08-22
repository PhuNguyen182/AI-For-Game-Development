---
name: dotween-tweening
description: >
  DOTween — the chained, component-shortcut Unity tweening engine:
  `DOTween.To()` (generic getter/setter tweens), Shortcuts
  (`transform.DOMove`, `material.DOColor`, and the full uGUI/TextMeshPro
  shortcut catalogue), `Sequence` (`Append`/`Join`/`Insert`/`Prepend`/
  `AppendCallback`), `Set-` chain methods (`SetEase`, `SetLoops`, `SetId`,
  `SetTarget`, `SetAutoKill`, `SetRecyclable`, `SetRelative`, `SetUpdate`),
  chained callbacks (`OnComplete`/`OnKill`/`OnUpdate`/etc.), instance and
  filtered-static control (`Play`/`Pause`/`Kill`/`DOTween.KillAll`),
  `DOPath`/`DOLocalPath` path tweens, Safe Mode and recycling, and both
  native (`AsyncWaitForCompletion`, `WaitForCompletion` coroutine waits)
  and UniTask-integrated (`UNITASK_DOTWEEN_SUPPORT`, `.ToUniTask()`-style
  await/`WithCancellation`) async support. Use for any code-authored
  interpolation of a value over time via DOTween specifically — including
  its uGUI/TextMeshPro shortcuts and its UniTask integration. This project
  also maintains a `litmotion-tweening` skill for the same job with a
  different (zero-allocation) engine; which one governs new work is a
  standing per-module/project decision, never assumed by this skill alone
  — see its own `coexistence-and-migration.md`. Not for: LitMotion's own
  API surface (`litmotion-tweening`), general async orchestration beyond
  awaiting a tween (`unitask-async-programming`), uGUI component
  setup/layout/event-wiring beyond animating an existing component
  (`ugui`), reactive event streams (`r3-reactive-extensions`), shader/
  particle VFX (`vfx-particle-authoring`), physics-driven movement not
  expressed as a tween (`unity-3d-physics`/`unity-2d-physics`).
---

# DOTween — Chained Tweening for Unity

## Bundled resources

### References
Read-only context, loaded on demand so this file stays short.

| File | Contents | Read when |
|---|---|---|
| [root-links.md](references/root-links.md) | Documentation root, Free vs Pro distribution, topic→file map, disclosed gaps | Starting any task here, or confirming a fact against the live docs |
| [getting-started.md](references/getting-started.md) | Install/setup, Modules panel, `DOTween.Init`, Free vs Pro, supported value types, nomenclature | Adding DOTween to a project, or a shortcut seems to be missing |
| [tweeners-shortcuts-and-generic.md](references/tweeners-shortcuts-and-generic.md) | `DOTween.To()`, the Shortcuts concept, non-UI component shortcut catalogue, Punch/Shake/ToAlpha/ToArray/ToAxis/virtual tweens | Creating any tween, or deciding generic vs Shortcut |
| [ugui-and-tmp-shortcuts.md](references/ugui-and-tmp-shortcuts.md) | Every uGUI (`CanvasGroup`/`Graphic`/`Image`/`RectTransform`/etc.) and TextMeshPro (Pro) shortcut, `DOTweenTMPAnimator` | Animating any uGUI or TMP component — this skill's cross-reference into `ugui` |
| [sequences.md](references/sequences.md) | `DOTween.Sequence()`, `Append`/`Insert`/`Join`/`Prepend`, `AppendCallback` vs `async`/`await` | Composing more than one tween into a coordinated animation |
| [settings-and-callbacks.md](references/settings-and-callbacks.md) | Every `Set-` chain method, chained callbacks, global settings (`timeScale`, capacity) | Configuring easing, looping, update timing, or wiring a callback |
| [control-methods.md](references/control-methods.md) | Instance control (`Play`/`Pause`/`Kill`/etc.) and filtered static control (`DOTween.*All` by Id/Target) | Pausing, resuming, or killing a tween or a filtered group of them |
| [path-tweens.md](references/path-tweens.md) | `DOPath`/`DOLocalPath`, `PathType`/`PathMode`, `SetOptions`/`SetLookAt` | Moving an object along a multi-waypoint path |
| [safe-mode-recycling-and-performance.md](references/safe-mode-recycling-and-performance.md) | Safe Mode, recycling discipline, capacity/editor report, allocation model vs LitMotion | Deciding recycling policy, or a performance/allocation question arises |
| [async-and-unitask-integration.md](references/async-and-unitask-integration.md) | Coroutine waits, `AsyncWaitForCompletion`, `UNITASK_DOTWEEN_SUPPORT` — this skill's cross-reference into `unitask-async-programming` | Awaiting a tween's completion from any async or coroutine call site |
| [coexistence-and-migration.md](references/coexistence-and-migration.md) | The DOTween-vs-LitMotion decision checklist, DOTween→LitMotion migration pointer | Before writing a new tween in an area with no established convention |

## 1. Objective
Animate values — Transform, UI, material, audio, physics, or a path — through
DOTween's chained `Tweener`/`Sequence` API with deliberate easing/looping/
update-timing configuration, correct Safe Mode and recycling discipline,
and the right completion-awaiting mechanism for the call site — without
silently defaulting DOTween as "the" project tweening engine over
`litmotion-tweening` when that choice was never actually made, holding a
reference to a recycled tween past its `OnKill`, or leaving `SetUpdate`
at a default that ties a pause-menu animation to a timescale it shouldn't
respect.

## 2. Role
Act as the DOTween specialist for the client track — the tool reached for
whenever a feature needs a chained, Shortcut-driven interpolation of a
value over time using DOTween specifically: a UI transition, a transform
move/path, a camera/audio parameter fade, a per-character text reveal, or
a punch/shake feedback effect. You never decide, on your own, whether
DOTween or LitMotion governs a given feature — that is a standing
project/module decision per
[coexistence-and-migration.md](references/coexistence-and-migration.md).

## 3. When to invoke this skill
- Animating a built-in or component-specific value (Transform, Material, uGUI, TextMeshPro Pro, Camera, Light, Rigidbody/Rigidbody2D, SpriteRenderer, AudioSource/AudioMixer) via a DOTween Shortcut or `DOTween.To()`.
- Composing several tweens into a coordinated `Sequence`.
- Configuring easing, looping, update timing (`SetUpdate`), or auto-kill/recycling behavior on an existing tween.
- Controlling (pausing/resuming/killing) one tween or a filtered group of them by Id/Target.
- Moving an object along a multi-waypoint path with `DOPath`/`DOLocalPath`.
- Awaiting a tween's completion from a coroutine, an `async` method, or via UniTask's native DOTween support.
- Porting existing DOTween code, or assessing whether a DOTween-specific feature (path tweens, `SetSpeedBased()`, DOTween Pro's TMP/visual-Sequence tooling) is the actual reason to reach for this engine over LitMotion.
- Negative trigger: the task is equally satisfied by either tweening engine and neither is already established for the touched module — that's a standing choice per [coexistence-and-migration.md](references/coexistence-and-migration.md), not something to decide by which skill got invoked; check convention or ask before writing code.
- Negative trigger: LitMotion's own `MotionBuilder`/`MotionHandle` API surface, or a zero-allocation/Burst requirement already pointing there — that's `litmotion-tweening`.
- Negative trigger: general async orchestration with no tween involved, or the cancellation-token/`PlayerLoopTiming`/multi-awaiter mechanics behind awaiting one — that's `unitask-async-programming`; this skill covers only the DOTween-specific await surface.
- Negative trigger: uGUI component setup, layout, or event wiring that isn't animating an existing component — that's `ugui`; this skill only animates components `ugui` already builds and wires.
- Negative trigger: a general reactive event/state stream unrelated to a timed interpolation — that's `r3-reactive-extensions`.
- Negative trigger: a shader-driven or particle-system visual effect — that's `vfx-particle-authoring`/`technical-artist`.
- Negative trigger: physically simulated movement driven by forces/collisions rather than a fixed-duration interpolation — that's `unity-3d-physics`/`unity-2d-physics` (DOTween's own `Rigidbody`/`Rigidbody2D` shortcuts move via physics but are still a scripted tween, not a force simulation — the negative trigger is force/collision-driven movement with no tween involved at all).
- Negative trigger: any `Game.Core.*` code — DOTween depends on `UnityEngine`, which `coding-principles.md`'s Shared Core integrity section forbids in Core. Drive Core state changes from `Game.Client.*` tweens instead.

## 4. How to use this skill
1. **Confirm which tweening engine governs this work before writing any tween code** — check the touched module's existing convention, then any stated project-wide choice, then ask if genuinely neither exists; never default to DOTween just because this skill was the one invoked, per [coexistence-and-migration.md](references/coexistence-and-migration.md).
2. **Confirm the Modules panel and Free-vs-Pro tier actually cover what's needed** — a uGUI feature needs `DOTweenModuleUI` enabled; a TMP or visually-authored Sequence feature needs DOTween Pro specifically, per [getting-started.md](references/getting-started.md).
3. **Reach for a Shortcut before the generic `DOTween.To()`** — it needs no getter/setter pair and, for any uGUI or TextMeshPro component, is documented in [ugui-and-tmp-shortcuts.md](references/ugui-and-tmp-shortcuts.md); fall back to generic only for a private/static/otherwise-unshortcut-able value, per [tweeners-shortcuts-and-generic.md](references/tweeners-shortcuts-and-generic.md).
4. **When animating a uGUI component, check `ugui`'s own ownership of that component first** — a `DOSizeDelta`/`DOFlexibleSize` tween fighting a Layout Group/Content Size Fitter over the same `RectTransform` property is a silent conflict, not a DOTween bug, per [ugui-and-tmp-shortcuts.md](references/ugui-and-tmp-shortcuts.md).
5. **Compose multi-step animation with a `Sequence`, and reach for `async`/`await` instead of `AppendCallback` once mid-animation logic needs branching or must propagate an exception** — per [sequences.md](references/sequences.md).
6. **Set `SetUpdate`'s `ignoreTimeScale` deliberately for anything that must animate while gameplay is paused** (a pause menu, a "Game Over" fade) — the default ties every tween to `Time.timeScale`, which is silently wrong for that case, per [settings-and-callbacks.md](references/settings-and-callbacks.md).
7. **Filter static control (`DOTween.PlayAll`/`KillAll`/etc.) by `SetId`/`SetTarget` rather than calling the unfiltered form** — an unfiltered `KillAll()` touches every tween in the project, including ones the calling code has no knowledge of, per [control-methods.md](references/control-methods.md).
8. **Leave Safe Mode on unless the platform specifically requires otherwise**, and null any held reference to a recyclable tween inside its own `OnKill` — a recycled tween's C# reference is reused for a future, unrelated tween, per [safe-mode-recycling-and-performance.md](references/safe-mode-recycling-and-performance.md).
9. **Await completion through UniTask's native `UNITASK_DOTWEEN_SUPPORT` integration whenever `unitask-async-programming` already governs the project's async style**, tying cancellation to the same `GetCancellationTokenOnDestroy()` discipline that skill already requires; fall back to `AsyncWaitForCompletion()` only where UniTask is genuinely unavailable, checking the documented WebGL caveat first, per [async-and-unitask-integration.md](references/async-and-unitask-integration.md).
10. **Reach for `DOPath`/`DOLocalPath` only when the motion genuinely follows multiple waypoints**, picking `PathType` and `resolution` deliberately rather than defaulting `CubicBezier` for a route `Linear`/`CatmullRom` would express more simply, per [path-tweens.md](references/path-tweens.md) and KISS in `coding-principles.md`.
11. **Verify a claimed allocation/performance advantage with the Profiler before it drives the DOTween-vs-LitMotion choice**, per `performance-and-algorithms.md`'s Verification section and [safe-mode-recycling-and-performance.md](references/safe-mode-recycling-and-performance.md) — a hot-path volume claim is a real reason to prefer LitMotion, but only once measured, not assumed.
12. **If the project's async ecosystem, target platform (WebGL caveat), or the DOTween-vs-LitMotion convention for this area is unstated, ask before committing to a mechanism** — all three gate a real decision and are expensive to unwind once tween code ships against the wrong assumption.

## 5. Specific goals / tasks this skill performs
- Creating and configuring a tween via a Shortcut or `DOTween.To()`, including uGUI/TextMeshPro shortcuts and `DOTweenTMPAnimator` per-character animation.
- Composing a `Sequence` from multiple tweens, callbacks, and intervals.
- Configuring easing, looping, update timing, relative values, auto-kill, and recycling via the `Set-` chain.
- Controlling one tween or a filtered group via instance or static `DOTween.*` methods.
- Building a multi-waypoint `DOPath`/`DOLocalPath` movement.
- Wiring completion-awaiting through a coroutine wait, `AsyncWaitForCompletion()`, or UniTask's native DOTween support.
- Assessing whether DOTween or LitMotion should govern a given piece of new tweening work, and porting DOTween code per the migration pointer.
- Out of scope: LitMotion's own API (`litmotion-tweening`), non-tween async orchestration (`unitask-async-programming`), uGUI component construction/layout/wiring (`ugui`), reactive stream composition (`r3-reactive-extensions`), shader/particle VFX (`vfx-particle-authoring`), physics simulation without a tween involved (`unity-3d-physics`/`unity-2d-physics`), any `Game.Core.*` usage.

## 6. Output format
```
## DOTween Work — <animation/feature name>
- Engine choice: DOTween confirmed over LitMotion — convention followed / explicitly decided / asked
- Creation: <Shortcut used, or DOTween.To() with reason>, module(s) required, Free/Pro confirmed
- uGUI/TMP interop: <component(s) animated, and ugui's ownership of layout/sizing confirmed not to conflict — or "n/a">
- Composition: <Sequence Append/Join/Insert/Prepend, or single tween>
- Configuration: <Ease/Loops/Id/Target/AutoKill/Recyclable/Relative/Update set, and why each>
- Control: <static filter used (Id/Target), or "n/a">
- Completion handling: <UniTask native await / AsyncWaitForCompletion / coroutine WaitFor*> — matches call site
- Safe Mode & recycling: <confirmed on / platform exception noted>; <OnKill nulling confirmed if recyclable>
- Verification: <Profiler allocation check confirmed, or "not applicable">
- Layer: Game.Client.* — never Game.Core.*
- Known limitations: <...>
```

**Extended report — emit ONLY when the requester asks for it.** It replaces
the one-line `Known limitations` above with all three fields:
```
- Known limitations: <what this animation/integration does not cover>
- Latent concerns: <assumptions holding only under current volume/platform/convention>
- Future remediation: <the concrete fix for each, and its trigger condition>
```

## 7. Examples
**Example 1**
- Input: a settings panel needs to fade in and slide up when opened, and the project's existing panels all use DOTween for this already.
- Output: followed existing convention (no need to ask, per step 1) — `canvasGroup.DOFade(1f, 0.3f).SetEase(Ease.OutQuad)` joined with `rectTransform.DOAnchorPosY(targetY, 0.3f)` in one `Sequence`, `SetUpdate(UpdateType.Normal, ignoreTimeScale: false)` left at default since this panel doesn't need to animate through a pause.

**Example 2**
- Input: "just use DOTween for this new inventory grid's item-appear animation, it's simpler."
- Output: checked first — the inventory module has no existing tweening code and the project has no stated convention between DOTween and LitMotion. Per [coexistence-and-migration.md](references/coexistence-and-migration.md), flagged this rather than defaulting to DOTween, and asked which engine should govern the inventory module before writing the animation.

**Example 3**
- Input: a boss intro needs to move an object through five waypoints, pause on the last one for a UI beat, then continue.
- Output: `DOPath` with `PathType.CatmullRom` and `PathMode.3D` for the waypoint traversal (`Linear` would look mechanical for this intro, so the extra smoothing is deliberate, not default), composed into a `Sequence` with `AppendInterval` for the pause; UI beat driven via `async`/`await` around the Sequence's UniTask-native await rather than `AppendCallback`, since it needs to `await` a separate Addressables load mid-beat, per [async-and-unitask-integration.md](references/async-and-unitask-integration.md).

**Example 4**
- Input: hundreds of simultaneously tweened bullet-hell projectile colors need updating every frame at high volume.
- Output: flagged this as a hot-path/high-volume case per [safe-mode-recycling-and-performance.md](references/safe-mode-recycling-and-performance.md) and [coexistence-and-migration.md](references/coexistence-and-migration.md) — recommended `litmotion-tweening` for this specific system instead of DOTween, pending a Profiler comparison to confirm the allocation difference actually matters at the project's real projectile count before committing either way.

## 8. Edge cases & guardrails
- Never assume DOTween governs new tweening work just because this skill was invoked — check module convention, then project convention, then ask, per [coexistence-and-migration.md](references/coexistence-and-migration.md).
- Never call a shortcut from a Module that isn't enabled, or promise a TMP/visual-Sequence feature without confirming DOTween Pro specifically is installed.
- Never let a DOTween tween and a `ugui` Layout Group/Content Size Fitter drive the same `RectTransform` property simultaneously.
- Never leave `SetUpdate`'s time-scale behavior at its default for an animation that must play while the game is paused.
- Never call an unfiltered `DOTween.KillAll()`/`CompleteAll()` etc. as a cleanup reflex — filter by `SetId`/`SetTarget`.
- Never hold a reference to a `SetRecyclable(true)` tween without nulling it in `OnKill` — a recycled tween's reference gets reused for an unrelated future tween.
- Never rely on `AsyncWaitForCompletion()` on a WebGL target without checking the documented freeze caveat; prefer UniTask's native integration wherever `unitask-async-programming` already governs the project.
- Never place DOTween types in `Game.Core.*` — the package depends on `UnityEngine`; drive Core state changes from `Game.Client.*` instead.
- Never claim an allocation/performance reason to prefer DOTween or LitMotion without a Profiler measurement backing it, per `performance-and-algorithms.md`.
- If the DOTween-vs-LitMotion convention for the touched area, the async ecosystem, or the target platform (WebGL) is unstated, ask rather than silently picking one — each gates a real, hard-to-unwind decision.
