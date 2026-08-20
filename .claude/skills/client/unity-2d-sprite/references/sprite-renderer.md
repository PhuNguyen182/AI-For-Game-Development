# Sprite Renderer Component

Sources: https://docs.unity3d.com/Manual/sprite/renderer/sprite-renderer-reference.html, https://docs.unity3d.com/Manual/sprite/profiler-2d.html, `UnityEngine.SpriteRenderer` scripting API

## Inspector properties

| Property | Description |
|---|---|
| Sprite | The `Sprite` asset this renderer draws. |
| Color | Tints the sprite; white renders it untinted. |
| Flip X / Flip Y | Mirrors the rendered texture on an axis without changing the GameObject's Transform — use this instead of a negative Transform scale, which also inverts child colliders/physics in ways Flip X/Y doesn't. |
| Draw Mode | **Simple** — uniform scaling of the whole sprite. **Sliced** — 9-slice stretch (see [nine-slicing.md](nine-slicing.md)). **Tiled** — 9-slice repeat. |
| Mask Interaction | **None** / **Visible Inside Mask** / **Visible Outside Mask** — see [sprite-mask.md](sprite-mask.md). |
| Sprite Sort Point | **Center** or **Pivot** — which point on the sprite is used when distance-from-camera is the active sort tie-breaker (see [sorting-sprites.md](sorting-sprites.md)). |
| Material | Defaults to `Sprite-Lit-Default` (URP) — swap only when a specific shader requirement (custom shader, unlit, a Technical Artist–authored effect) calls for it; owning shader authoring itself is `technical-artist`'s/`shader-authoring`'s territory. |
| Sorting Layer / Order in Layer (Additional Settings) | See [sorting-sprites.md](sorting-sprites.md). |
| Rendering Layer Mask | Assigns the GameObject to rendering layers, e.g. for `Light2D` layer filtering — owning the lighting-side setup is `unity-urp-rendering`'s territory. |

## Scripting API surface

| Member | Description |
|---|---|
| `sprite` | The rendered `Sprite` reference — reassign to swap art (e.g. a placeholder → final art swap, or a state-driven sprite change; see [placeholder-sprites.md](placeholder-sprites.md)). |
| `color`, `flipX`, `flipY` | Same as the Inspector fields. |
| `drawMode`, `size`, `tileMode`, `adaptiveModeThreshold` | Script-side equivalents of Draw Mode/Sliced-Tiled sizing/fill controls. |
| `maskInteraction`, `spriteSortPoint` | Script-side equivalents of the Inspector fields. |
| `sortingLayerName` / `sortingLayerID`, `sortingOrder` | Script-side sorting layer/order control. |
| `GetBlendShapeWeight`/`SetBlendShapeWeight` | For sprites with blend-shape data (2D Animation package content) — out of scope for this skill. |
| `RegisterSpriteChangeCallback`/`UnregisterSpriteChangeCallback` | Subscribe to the renderer's `sprite` reference changing — unsubscribe on the same lifecycle boundary the change was registered on, per `coding-principles.md`'s Event handlers rule. |

## 2D Profiler module

**Window > Analysis > Profiler**, enable the **2D** module. Tracks Sprite Count / SpriteAtlas Count (loaded, including culled) vs. Sprites Rendered / SpriteAtlases Rendered (actually drawn), plus a details pane showing each atlas/sprite/texture's **Usage** — the percentage of a packed atlas actually contributing to what's on screen. A low Usage percentage on a resident atlas is a direct signal of wasted GPU memory — see [sprite-atlas.md](sprite-atlas.md)'s grouping guidance.

## Practical guidance

- Reassigning `sprite` at runtime (state-driven sprite swaps, hit-flash color changes via `color`) is fine as a Unity-side visual-feedback response — but the *decision* of which state/sprite to show belongs in Shared Core's state machine per `coding-principles.md`'s Shared Core integrity rule; this component only renders whatever state Core already resolved.
- Never call `GetComponent<SpriteRenderer>()` inside `Update()`/hot-path code — cache the reference once, per the baseline performance rule in `coding-principles.md`.
- Only update `color`/`sprite`/sorting fields when the underlying value actually changed, matching `performance-and-algorithms.md`'s "only update UI/visuals when the value changed" rule — reassigning an unchanged `Sprite` reference or repainting an identical tint every frame is wasted work.
