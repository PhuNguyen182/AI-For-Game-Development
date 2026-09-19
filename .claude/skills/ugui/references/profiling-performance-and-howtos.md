# UI Profiler, Batching, and Common How-Tos

Source: [UI Profiler](https://docs.unity3d.com/Packages/com.unity.ugui@2.6/manual/ProfilerUI.html), [Designing UI for Multiple Resolutions](https://docs.unity3d.com/Packages/com.unity.ugui@2.6/manual/HOWTO-UIMultiResolution.html), [Creating a World Space UI](https://docs.unity3d.com/Packages/com.unity.ugui@2.6/manual/HOWTO-UIWorldSpace.html), [Creating UI elements from scripting](https://docs.unity3d.com/Packages/com.unity.ugui@2.6/manual/HOWTO-UICreateFromScripting.html).
Covers: SKILL.md §4 — "Read Self/Cumulative Batch Count before guessing at a batching regression", "Prefab-instantiate UI from script, don't hand-build a hierarchy in code".

## UI (Canvas) Profiler module

Reports, per Canvas: **Self Batch Count** (batches this canvas alone
generates) and **Cumulative Batch Count** (including nested canvases),
plus per-batch vertex counts and participating GameObjects in the Details
pane. This is **Editor-only profiling data** — it does not function in a
development build, so a batching claim made from an Editor session alone
is an Editor-only result, per `verification-standards.md`'s rule on
labelling Editor results as indicative.

### What breaks a batch

| Cause | Why |
|---|---|
| Non-coplanar geometry | Elements must be unrotated relative to the canvas to stay in the same batch |
| A `CanvasGroup` in the hierarchy | Forces a new batch for everything under it — the Manual's own example is a dropdown's option list |
| Material/texture mismatch | Elements need identical materials, masking state, textures, and texture alpha-channel usage to batch together |

This is consistent with `performance-and-algorithms.md`'s general Unity
rendering guidance (reduce draw calls, use `MaterialPropertyBlock` for
per-instance variation) — the uGUI-specific addition is that a `Mask`
(stencil-based, see [visual-components.md](visual-components.md)) and a
`CanvasGroup` are both documented batch-break triggers on top of the usual
material/texture rules, so a mask or a fade wrapper on a large,
frequently-visible subtree is a deliberate cost to weigh, not a free
convenience wrapper.

### Practical canvas-splitting guidance

Not explicitly spelled out on the fetched `ProfilerUI.html` page itself,
but it follows directly from how Canvas rebuilds work and from
`performance-and-algorithms.md`'s own UI guidance (originally written
for UI Toolkit's Canvas-rebuild equivalent, and equally true here): any
change to one element inside a Canvas forces Unity to rebuild that
Canvas's whole batch geometry. Put a frequently-updating element (a
health bar, a timer) on its own `Canvas`, separate from static menu
chrome, so its updates don't force a rebuild of content that never
changed.

## How-tos

### Designing UI for multiple resolutions

Combine anchors (per [rect-transform-and-layout.md](rect-transform-and-layout.md))
with `CanvasScaler` (per [canvas-and-scaling.md](canvas-and-scaling.md)):
anchor elements to the screen corners/edges they should track, and set
`CanvasScaler`'s `Match` slider to **0.5** rather than leaving it at the
default **0** (Width) once both portrait and landscape (or several aspect
ratios) must be supported — the documented failure mode is a landscape
resolution scaling everything oversized when `Match` stays at 0.

### Creating a World Space UI

1. Create a UI element (auto-creates a `Canvas` if none exists).
2. Set that `Canvas`'s Render Mode to **World Space**.
3. Set a pixel resolution on its `RectTransform` (e.g. 800×600 as a
   reasonable baseline).
4. Compute a uniform scale from a target real-world size:
   `scale = target_meters_wide / canvas_pixel_width` (e.g. `2 / 800 =
   0.0025` for a 2-meter-wide panel), applied uniformly to X/Y/Z.
5. Position/rotate the canvas like any other scene object — unlike a
   Screen Space canvas, it can be freely placed on a wall, floor, or held
   surface.
6. Build the UI inside it using the same components as any other canvas.

Confirm which camera/raycaster setup a World Space canvas needs for
pointer input on the live Manual page before promising exact event-camera
wiring — that mechanic wasn't independently re-verified for this skill
(see [root-links.md](root-links.md)'s Disclosed gaps).

### Creating UI elements from scripting

The documented pattern is **prefab instantiation, not building a
hierarchy from bare `AddComponent` calls at runtime**: author the element
(e.g. a styled button) once as a prefab in the Scene/Project, then at
runtime `Instantiate()` it and `Transform.SetParent(parent, false)` (the
`false` keeps `worldPositionStays` off, which is what preserves the
prefab's local `RectTransform` values instead of recomputing a world-space
placement). Position a non-stretching instance via `anchoredPosition` +
`sizeDelta`; position a stretching one via `offsetMin`/`offsetMax`. Reach
for `GetComponent<T>()` on the instantiated root to customize per-instance
values (text, sprite, bound data) after instantiation.

Prefer this over constructing a UI element purely in code — per KISS in
`coding-principles.md`, a prefab is inspectable, diffable, and editable by
a designer, where a hand-built hierarchy in C# is none of those.
