# Sprite Renderer — Component, Scripting Surface & the 2D Profiler

Sources: [Sprite Renderer component reference](https://docs.unity3d.com/Manual/sprite/renderer/sprite-renderer-reference.html), [2D Profiler module](https://docs.unity3d.com/Manual/sprite/profiler-2d.html).
Covers: SKILL.md §4 — **"Keep the sprite layer free of decisions"**, **"Confirm any draw-call or overdraw claim with the Profiler's 2D module before reporting it"**.

`SpriteRenderer` draws a `Sprite` and nothing more: it renders state that
`Game.Core.*` has already resolved, per `coding-principles.md`'s Shared Core
integrity section. This file holds its fields, its scripting surface, and the
Profiler module that turns a claimed batching win into a measured one.

## Inspector

| Property | What it decides | Source |
|---|---|---|
| Sprite | The drawn asset; reassigning is the sprite-swap path | [Sprite Renderer reference](https://docs.unity3d.com/Manual/sprite/renderer/sprite-renderer-reference.html) |
| Color | Tint, applied as vertex colour — so unlike a `MaterialPropertyBlock` it does not cost the renderer its batch | [Sprite Renderer reference](https://docs.unity3d.com/Manual/sprite/renderer/sprite-renderer-reference.html) |
| Flip X / Flip Y | Mirrors the drawn texture without touching the Transform — the correct alternative to negative scale, which also inverts child colliders | [Sprite Renderer reference](https://docs.unity3d.com/Manual/sprite/renderer/sprite-renderer-reference.html) |
| Draw Mode | Simple ignores the sprite's border; Sliced and Tiled activate 9-slicing, see [nine-slicing.md](nine-slicing.md) | [Sprite Renderer reference](https://docs.unity3d.com/Manual/sprite/renderer/sprite-renderer-reference.html) |
| Mask Interaction | Whether and how a `SpriteMask` affects this renderer — see [sprite-mask.md](sprite-mask.md) | [Sprite Renderer reference](https://docs.unity3d.com/Manual/sprite/renderer/sprite-renderer-reference.html) |
| Sprite Sort Point | Center or Pivot, used only when distance is the active tie-breaker — see [sorting-sprites.md](sorting-sprites.md) | [Sprite Renderer reference](https://docs.unity3d.com/Manual/sprite/renderer/sprite-renderer-reference.html) |
| Material | `Sprite-Lit-Default` under URP; swapping it is a shader decision owned by `shader-authoring` | [Sprite Renderer reference](https://docs.unity3d.com/Manual/sprite/renderer/sprite-renderer-reference.html) |
| Sorting Layer / Order in Layer | Position in the sort chain — see [sorting-sprites.md](sorting-sprites.md) | [Sprite Renderer reference](https://docs.unity3d.com/Manual/sprite/renderer/sprite-renderer-reference.html) |
| Rendering Layer Mask | Which rendering layers apply, e.g. for `Light2D` filtering owned by `unity-urp-rendering` | [Sprite Renderer reference](https://docs.unity3d.com/Manual/sprite/renderer/sprite-renderer-reference.html) |

## Scripting

| Member | What it decides | Source |
|---|---|---|
| `sprite` | The drawn asset; assign only when the value actually changed, per `performance-and-algorithms.md`'s only-update-on-change rule | [Sprite Renderer reference](https://docs.unity3d.com/Manual/sprite/renderer/sprite-renderer-reference.html) |
| `color`, `flipX`, `flipY` | Script equivalents of the Inspector fields | [Sprite Renderer reference](https://docs.unity3d.com/Manual/sprite/renderer/sprite-renderer-reference.html) |
| `drawMode`, `size`, `tileMode`, `adaptiveModeThreshold` | Runtime control of Sliced/Tiled sizing and the Adaptive stretch threshold | [Sprite Renderer reference](https://docs.unity3d.com/Manual/sprite/renderer/sprite-renderer-reference.html) |
| `maskInteraction`, `spriteSortPoint` | Script equivalents of the masking and sort-point fields | [Sprite Renderer reference](https://docs.unity3d.com/Manual/sprite/renderer/sprite-renderer-reference.html) |
| `sortingLayerName` / `sortingLayerID`, `sortingOrder` | Runtime sorting control; the ID overload avoids the per-call string lookup the name overload performs | [Sprite Renderer reference](https://docs.unity3d.com/Manual/sprite/renderer/sprite-renderer-reference.html) |
| `RegisterSpriteChangeCallback` / `UnregisterSpriteChangeCallback` | Observes `sprite` reassignment; unregister on the same lifecycle boundary that registered, per `coding-principles.md`'s Event handlers section | [Sprite Renderer reference](https://docs.unity3d.com/Manual/sprite/renderer/sprite-renderer-reference.html) |

## 2D Profiler module

| Counter | What it decides | Source |
|---|---|---|
| Sprite Count vs Sprites Rendered | Loaded versus actually drawn — a large gap means sprites are resident for content that is culled | [2D Profiler module](https://docs.unity3d.com/Manual/sprite/profiler-2d.html) |
| SpriteAtlas Count vs SpriteAtlases Rendered | The same gap at atlas granularity, which is the direct test of a co-visibility grouping | [2D Profiler module](https://docs.unity3d.com/Manual/sprite/profiler-2d.html) |
| Usage % per atlas | How much of a resident atlas contributes to the frame — a low value is the measurement that condemns a grouping, see [sprite-atlas.md](sprite-atlas.md) | [2D Profiler module](https://docs.unity3d.com/Manual/sprite/profiler-2d.html) |

Open it from **Window > Analysis > Profiler** and enable the **2D** module.
