# Known Issues & Platform Caveats — engine bugs OSA sits on top of

Source: [OSA 6.0–7.0 Complete Manual](https://forbiddenbyte.com/blog/osa-complete-manual/) (Known issues, workarounds; Tips; FAQ), plus the upstream Unity pages and forum threads it cites.
Covers: SKILL.md §4 — **"Let OSA initialize from `Start()` unless you call `Init()` yourself, and never assume a correct viewport size inside `Awake()`"**, **"Decide the item-size strategy before the item prefab is authored"**.

Almost every entry here is a Unity-version or platform bug that *presents*
as an OSA bug. Read this before writing a workaround: a hand-rolled fix for
one of these hides the real cause and survives long past the engine version
that needed it. Canvas and mask component setup itself belongs to `ugui`;
this file only records where those components misbehave under OSA.

## Initialization and sizing

| Symptom | Cause and what to do | Source |
|---|---|---|
| Scroll view reports a wrong size, and a `ScrollTo` right after init lands in the wrong place — grids especially | `RectTransform` does not report its size correctly inside `Awake()` on several Unity versions (2018.4.9, 2018.4.34, 2019.4.10 among others), particularly when anchors are not brought together. General fix: initialize OSA in `Start()`, not `Awake()`. Narrow fix for the `ScrollTo` case only: use `SmoothScrollTo` with a duration of 0 instead | [Manual — Known issues](https://forbiddenbyte.com/blog/osa-complete-manual/) |
| Need data set on the same frame the OSA prefab is instantiated | Call `OSA.Init()` manually before setting data, guarding on `OSA.IsInitialized` if it may already have run; or override `Awake()` and call `Init()` there — OSA detects that and skips its own auto-init in `Start()`. `Awake()` only runs if the GameObject is active | [Manual — FAQ 14](https://forbiddenbyte.com/blog/osa-complete-manual/) |
| A `OSAContentDecorator` is missing or throws when OSA is initialized manually | The decorator must initialize *before* OSA does. Call `<decorator>.Init()` explicitly before `OSA.Init()` | [Manual — FAQ 18](https://forbiddenbyte.com/blog/osa-complete-manual/) |

## ContentSizeFitter prefab traps

These bite while choosing the item-size strategy, not after — they constrain
how the prefab must be authored. See [variable-item-sizes.md](variable-item-sizes.md)
for the twin-pass mechanism itself.

| Trap | Cause and what to do | Source |
|---|---|---|
| Item text is oddly truncated on some Unity versions | The prefab's `Text` had **Vertical Overflow** set to `Truncate`. Set it to `Overflow` as a general rule under a CSF. For a horizontal scroll view, **Horizontal Overflow** is the one to change | [Manual — Known issues](https://forbiddenbyte.com/blog/osa-complete-manual/) |
| Adapter fails to initialize an item correctly when children are toggled | A GameObject under the CSF whose active state at edit time disagrees with what the code sets on the first frame after init. Author the prefab in the state the first frame will produce: keep it disabled if it is disabled immediately, enabled if it is enabled | [Manual — Known issues](https://forbiddenbyte.com/blog/osa-complete-manual/), [forum post](https://forum.unity.com/threads/optimized-scrollview-adapter-listview-gridview.395224/page-4#post-3525615) |

## Masking and rendering

| Symptom | Cause and what to do | Source |
|---|---|---|
| Items are not clipped to the Viewport | Some Unity versions ship a broken `RectMask2D` — confirmed for WebGL builds on 2018.1/2018.2 when the Canvas is not in Overlay space, and plausible on others. Replace it with the older `Mask` + `Image` pair for that build | [Manual — Known issues](https://forbiddenbyte.com/blog/osa-complete-manual/) |
| Choosing between `Mask` and `RectMask2D` in the first place | Prefer `RectMask2D` — it is faster for scroll views whenever masking by an arbitrary shape is not required. Test per platform because of the bug above | [Manual — Tips](https://forbiddenbyte.com/blog/osa-complete-manual/) |
| Frequently changing UI forces whole-Canvas rebuilds | Parent groups of frequently changing elements under their own nested `Canvas` to isolate them from static chrome. This is standard uGUI batching hygiene, owned by `ugui`, and it matters here because a scrolling list changes every frame | [Manual — Tips](https://forbiddenbyte.com/blog/osa-complete-manual/), [Unity UI optimization tips](https://create.unity3d.com/Unity-UI-optimization-tips) |
| Setting an `Image.sprite` from script misbehaves | A Unity 2019.1/2019.2 bug, unrelated to OSA | [forum thread](https://forum.unity.com/threads/changing-image-sprite-from-script-is-faulty-in-2019-1-0f2-case-1146947.663478/) |

## Build targets

| Target | Caveat | Source |
|---|---|---|
| WebGL | High managed-code stripping produces a "call stack size exceeded" `RangeError` at runtime. Add OSA's namespaces to the project's `link.xml` manually | [Manual — Known issues](https://forbiddenbyte.com/blog/osa-complete-manual/), [forum post](https://forum.unity.com/threads/optimized-scrollview-adapter-listview-gridview-playmaker-support.395224/page-7#post-4278724) |
| Android, older devices | `Gfx.WaitForPresent` eating 10–20 FPS on simple scenes — a Unity issue, not an OSA one; the vendor's fix was upgrading the Editor version | [Manual — Known issues](https://forbiddenbyte.com/blog/osa-complete-manual/) |
| Low-end devices generally | Terrible performance under OpenGL ES 3 / Auto Graphics API. Untick Auto Graphics API and target OpenGL ES 2 for those | [Manual — Known issues](https://forbiddenbyte.com/blog/osa-complete-manual/) |

## Input

| Symptom | Cause and what to do | Source |
|---|---|---|
| New Input System compatibility | OSA works under either input system (tested on 5.3.1 / Unity 2019.4 LTS). Only the `EventSystem` object needs migrating — the demo scenes deliberately ship on the old system for compatibility, so migrate them yourself if you run them | [Manual — FAQ 20](https://forbiddenbyte.com/blog/osa-complete-manual/), [Input System Installation](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.0/manual/Installation.html), [UI Support](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.0/manual/UISupport.html) |
| A custom component handling `OnPointerDown`/`OnPointerUp` blocks scrolling when dragged | A general Unity event-consumption problem, not OSA-specific. `InputFieldInScrollRectFixerBase` solves it for InputFields; model a custom component's event forwarding on that | [Manual — FAQ 25](https://forbiddenbyte.com/blog/osa-complete-manual/) |
| Button clicks fire while the content is still moving | Keep an invisible `Image` at the same hierarchy level as Content, enabled only while `OSA.Velocity` is non-zero — it blocks interaction with the items but still forwards drags to OSA. `CutMovementOnPointerDown` can usually stay on; turn it off if that combination misbehaves | [Manual — FAQ 21](https://forbiddenbyte.com/blog/osa-complete-manual/) |

**Critical caveat**: OSA's `Time` and `DeltaTime` properties are deliberately
named to shadow `UnityEngine.Time` inside an adapter, so that
`Params.UseUnscaledTime` governs your own animations too. An error like
`'float' does not contain a definition for 'time'` means you wrote `Time.time`
inside the adapter — use OSA's `Time`/`DeltaTime` for adapter-driven timing,
or qualify as `UnityEngine.Time` when you genuinely mean the engine clock.
