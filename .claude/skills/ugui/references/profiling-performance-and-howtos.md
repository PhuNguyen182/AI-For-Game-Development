# UI Profiler, Batching, How-Tos

## UI (Canvas) Profiler
Per Canvas: **Self Batch Count** (this canvas), **Cumulative Batch Count** (incl. nested canvases), per-batch vertex counts and GameObjects in Details. **Editor-only**: it does not work in a development build, so a batching claim from it is an Editor-only result.

| Batch breaker | Why |
|---|---|
| Non-coplanar geometry | Elements must be unrotated relative to the canvas |
| `CanvasGroup` | New batch for everything under it (e.g. a dropdown list) |
| Material/texture mismatch | Needs identical materials, masking state, textures, alpha-channel usage |
| `Mask` (stencil) | Breaks batches too; weigh a mask or fade wrapper on a large visible subtree |

## Canvas splitting
Inferred, not stated on the Profiler page: any change to one element rebuilds its Canvas's batch geometry. Put a frequently-updating element (health bar, timer) on its own `Canvas`, apart from static chrome. Also gate text updates on an actual value change rather than per-frame `.ToString()`.

## Multi-resolution
Anchor elements to the edges they track ([rect-transform-and-layout.md](rect-transform-and-layout.md)) and use `CanvasScaler` Scale With Screen Size with Match set per SKILL step 3 (stable axis; 0.5 only when both orientations ship) ([canvas-and-scaling.md](canvas-and-scaling.md)).

## World Space UI
1. Create a UI element (auto-creates a Canvas); set Render Mode World Space.
2. Set a pixel size on its `RectTransform` (e.g. 800x600).
3. Uniform scale = target meters wide / canvas pixel width (2 m / 800 = 0.0025), on X/Y/Z.
4. Place and rotate like any scene object; build UI with the usual components.

Unverified: the event camera / raycaster wiring for pointer input on a World Space canvas. Confirm on the live Manual before promising it.

## UI from script
Author the element once as a prefab, then `Instantiate()` and `SetParent(parent, false)` (false keeps the prefab's local `RectTransform` values). Non-stretching: `anchoredPosition` + `sizeDelta`; stretching: `offsetMin`/`offsetMax`. Customise per instance via `GetComponent<T>()` on the root. Do not build a hierarchy from bare `AddComponent` calls; a prefab is inspectable, diffable and designer-editable.
