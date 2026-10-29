# Known Issues & Platform Caveats

Sources: M = manual https://forbiddenbyte.com/blog/osa-complete-manual/ (Known issues, Tips, FAQ). Most entries are Unity-version or platform bugs that present as OSA bugs: check here before a workaround, which would hide the real cause.

| Symptom | Cause and action |
|---|---|
| Wrong size, `ScrollTo` right after init lands wrong (grids especially) | `RectTransform` misreports size in `Awake()` on several Unity versions (2018.4.9, 2018.4.34, 2019.4.10, others), esp. with unjoined anchors. Initialize in `Start()`. `ScrollTo` only: `SmoothScrollTo` with duration 0 |
| Data needed the frame the OSA prefab is instantiated | `Init()` manually, guard with `IsInitialized`; or `Init()` in `Awake()` (OSA then skips auto-init; `Awake()` needs an active GameObject) |
| Decorator missing or throws under manual init | Call `<decorator>.Init()` before `OSA.Init()` |
| Item text oddly truncated (ContentSizeFitter) | Prefab `Text` Vertical Overflow was `Truncate`; set `Overflow` (Horizontal Overflow for a horizontal view) |
| Item initializes wrongly when children toggle | Child active state at edit time disagrees with what code sets on the first frame; author the prefab in the first-frame state |
| Items not clipped to Viewport | Broken `RectMask2D` (confirmed WebGL 2018.1/2018.2, Canvas not Overlay; plausible elsewhere); use `Mask` + `Image` for that build. Otherwise prefer `RectMask2D`; test per platform |
| `Image.sprite` set from script misbehaves | Unity 2019.1/2019.2 bug, unrelated to OSA |
| WebGL: "call stack size exceeded" `RangeError` | High managed stripping; add OSA namespaces to `link.xml` |
| Android older devices: `Gfx.WaitForPresent` costs 10-20 FPS | Unity issue; vendor fix was upgrading the Editor |
| Low-end devices: terrible performance on OpenGL ES 3 / Auto Graphics API | Legacy Editors only: untick Auto Graphics API, target OpenGL ES 2. Unity 2023.1+ removed GLES2 — profile on Vulkan/GLES3 instead |
| Input System | Works under either (tested 5.3.1 / Unity 2019.4 LTS); only migrate the `EventSystem`. Demo scenes ship on the old input system |
| Custom `OnPointerDown`/`OnPointerUp` component blocks scrolling when dragged | General Unity event consumption; model forwarding on `InputFieldInScrollRectFixerBase` |
| Button clicks fire while content moves | Invisible `Image` at Content's hierarchy level, enabled while `OSA.Velocity` is non-zero (blocks items, forwards drags). `CutMovementOnPointerDown` can usually stay on; turn it off if the combination misbehaves |
