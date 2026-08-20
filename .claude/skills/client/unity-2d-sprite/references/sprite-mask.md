# Sprite Mask

Sources: https://docs.unity3d.com/Manual/sprite/mask/mask-landing.html, https://docs.unity3d.com/Manual/sprite/mask/hide-reveal-parts-sprite-mask.html, https://docs.unity3d.com/Manual/sprite/mask/sprite-mask-reference.html

## Concept

A `SpriteMask` hides or reveals parts of other sprites based on where it overlaps them. It's unrelated to a URP mask-map secondary texture (see [secondary-textures.md](secondary-textures.md)) — same word, different feature; don't confuse the two.

## Prerequisite

The active 2D Renderer asset must have its **Depth/Stencil Buffer** enabled — sprite masking is stencil-buffer-based and silently does nothing if that's off.

## Setting it up

1. **GameObject > 2D Object > Sprite Mask** (defaults to a circular mask shape — swap its Sprite reference for a custom shape: opaque pixels define the mask area, transparent pixels define the excluded area).
2. Position the mask so it overlaps the sprite(s) it should affect.
3. On each target `SpriteRenderer`, set **Mask Interaction**: **None** (unaffected by any mask), **Visible Inside Mask** (only the overlapping portion renders), or **Visible Outside Mask** (the overlapping portion is hidden, the rest renders).

## Sprite Mask component properties

| Property | Description |
|---|---|
| Mask Source | **Sprite** — mask shape comes from a `Sprite`. **Supported Renderer** — mask shape comes from an attached `SpriteRenderer`, `SpriteShapeRenderer`, or `TilemapRenderer` instead of a dedicated sprite. |
| Sprite | The masking sprite (Mask Source = Sprite only); opaque pixels define the masked area. |
| Supported Renderer | Which renderer component supplies the mask shape (Mask Source = Supported Renderer only). |
| Sprite Sort Point | **Center** or **Pivot** — which point on the mask sprite is used for camera-distance sorting (Mask Source = Sprite only). |
| Alpha Cutoff | Minimum alpha for a pixel to count as part of the mask shape — lower values include more semi-transparent pixels. |
| Custom Range | When enabled, restricts which Sorting Layers the mask affects via explicit Front/Back boundaries, instead of affecting every sprite it geometrically overlaps regardless of layer. |
| Front Sorting Layer / Order in Layer | The topmost layer+sublayer the mask affects — anything above this boundary is unmasked. |
| Back Sorting Layer / Order in Layer | The bottommost layer+sublayer the mask affects — this layer and anything behind it is unmasked. |
| Rendering Layer Mask | Restricts masking to GameObjects on matching rendering layers — independent of draw order/sorting layers. |

## Restricting which sprites a mask affects

Beyond `Mask Interaction`/`None` on individual renderers, use **Custom Range** with Sorting Layers to scope a mask to a specific band of the sort order — put the sprites that should never be maskable on a layer outside the mask's Front/Back range. For multiple independent masks that shouldn't interfere with each other, combine this with a [Sorting Group](sorting-sprites.md) around each mask+target set.

## Practical guidance

- If a mask appears to do nothing, check the 2D Renderer Data's Depth/Stencil Buffer setting first — it's the most common reason masking silently fails.
- Prefer **Custom Range** over relying purely on `Mask Interaction = None` on every non-target sprite when a scene has several masks — explicitly scoping each mask's range is more robust than remembering to opt every unrelated sprite out individually.
