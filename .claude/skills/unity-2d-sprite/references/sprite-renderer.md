# Sprite Renderer, 9-Slicing, Sprite Mask, 2D Profiler

Pages: https://docs.unity3d.com/Manual/sprite/renderer/sprite-renderer-reference.html, https://docs.unity3d.com/Manual/sprite/9-slice/9-slice-landing.html, https://docs.unity3d.com/Manual/sprite/mask/mask-landing.html, https://docs.unity3d.com/Manual/sprite/profiler-2d.html

## SpriteRenderer

| Property (script name) | Decision |
|---|---|
| Sprite (`sprite`) | Reassign to swap; assign only when changed |
| Color (`color`) | Tint as vertex colour, so unlike a `MaterialPropertyBlock` it keeps the batch |
| Flip X / Y (`flipX`, `flipY`) | Mirrors the texture without touching the Transform |
| Draw Mode (`drawMode`, `size`, `tileMode`, `adaptiveModeThreshold`) | Simple ignores the border; Sliced/Tiled activate 9-slicing |
| Mask Interaction (`maskInteraction`) | How a `SpriteMask` affects this renderer |
| Sprite Sort Point (`spriteSortPoint`) | Center or Pivot, used only when distance is the active tie-breaker |
| Material | `Sprite-Lit-Default` under URP; swapping is `shader-authoring`'s |
| Sorting Layer / Order (`sortingLayerName`/`sortingLayerID`, `sortingOrder`) | See sorting-sprites.md; the ID overload avoids the per-call string lookup |
| Rendering Layer Mask | e.g. `Light2D` filtering (`unity-urp-rendering`) |

`RegisterSpriteChangeCallback` / `UnregisterSpriteChangeCallback` observe `sprite` reassignment; unregister where registered.

## 9-slicing

Holds corners fixed while edges and centre absorb the resize. Needs both a Border on the sprite asset and a Draw Mode of Sliced/Tiled on the renderer; inert without both.

- Regions: 4 corners never stretch or tile; 4 edges stretch/tile on one axis; centre on both.
- Prerequisite: Mesh Type Full Rect (Tight silently breaks it).
- Border L/R/T/B (Sprite Editor): cover the frame detail and no more, since an oversized border shrinks the stretch regions.

| Option | Decision |
|---|---|
| Sliced | All regions scale; right for UI frames and gradients, blurs a patterned texture |
| Tiled — Continuous | Edges and centre repeat the pattern, never stretch; boundary tiles may be cropped |
| Tiled — Adaptive | Stretches until the Stretch Value multiple of original size, then repeats (Stretch Value 1 starts repeating when the sprite doubles) |

Only `BoxCollider2D` and `PolygonCollider2D` can follow a 9-sliced sprite, and only with **Auto Tiling** on; otherwise the collider keeps its shape from the last resize (`unity-2d-physics` configures it).

## SpriteMask

Hides or reveals other sprites where it overlaps, via the stencil buffer. Unrelated to a `_MaskTex` secondary texture. Takes effect only where the renderer's Mask Interaction and the mask's sorting range agree.

- **Prerequisite**: Depth/Stencil Buffer enabled on the active 2D Renderer Data, else masking silently does nothing. Check this first.
- Target `SpriteRenderer` Mask Interaction: **None** (default, so a new mask seems dead until targets opt in), **Visible Inside Mask** (only the overlap renders), **Visible Outside Mask** (overlap hidden).

| Property | Decision |
|---|---|
| Mask Source | **Sprite**, or **Supported Renderer** (`SpriteRenderer`, `SpriteShapeRenderer`, `TilemapRenderer`: how a tilemap or spline becomes a mask) |
| Alpha Cutoff | Minimum alpha counted as mask; lower pulls semi-transparent edges in |
| Sprite Sort Point | Center or Pivot, when distance is the tie-breaker |
| Custom Range | Limits the mask to a band of Sorting Layers (Front/Back Sorting Layer + Order in Layer); anything outside is unmasked |
| Rendering Layer Mask | Restricts masking by rendering layer, independent of draw order |

Prefer Custom Range over opting unrelated sprites out one by one (opt-outs must be repeated for every sprite added later). Add a Sorting Group around each mask-and-target set when several masks must stay independent.

## 2D Profiler module

Window > Analysis > Profiler, enable **2D**.

| Counter | Reads |
|---|---|
| Sprite Count vs Sprites Rendered | Loaded vs drawn; a large gap means sprites resident for culled content |
| SpriteAtlas Count vs SpriteAtlases Rendered | Same gap per atlas; tests a co-visibility grouping |
| Usage % per atlas | Share of a resident atlas contributing to the frame; low condemns a grouping |
