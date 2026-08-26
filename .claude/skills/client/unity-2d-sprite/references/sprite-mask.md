# Sprite Mask — Stencil-Based Reveal & Hide

Sources: [Add a sprite mask](https://docs.unity3d.com/Manual/sprite/mask/hide-reveal-parts-sprite-mask.html), [Sprite Mask component reference](https://docs.unity3d.com/Manual/sprite/mask/sprite-mask-reference.html).
Covers: SKILL.md §4 — **"Reach for 9-slicing or `SpriteMask` only when the design actually resizes or reveals something"**.

A `SpriteMask` hides or reveals other sprites where it overlaps them, using
the stencil buffer. It is unrelated to a `_MaskTex` secondary texture despite
the shared word — see [secondary-textures.md](secondary-textures.md). Masking
takes effect only where two independent settings agree: the renderer's Mask
Interaction, and the mask's own sorting-layer range.

## Prerequisite

| Requirement | Consequence if unmet | Source |
|---|---|---|
| Depth/Stencil Buffer enabled on the active 2D Renderer Data | Masking silently does nothing at all — no warning, no visual change; this is the usual cause before any component setting is suspect | [Add a sprite mask](https://docs.unity3d.com/Manual/sprite/mask/hide-reveal-parts-sprite-mask.html) |

## Component properties

| Property | What it decides | Source |
|---|---|---|
| Mask Source | **Sprite** takes the shape from a `Sprite`; **Supported Renderer** takes it from an attached `SpriteRenderer`, `SpriteShapeRenderer`, or `TilemapRenderer` — the latter is how a tilemap or spline shape becomes a mask | [Sprite Mask component reference](https://docs.unity3d.com/Manual/sprite/mask/sprite-mask-reference.html) |
| Sprite | The masking shape; opaque pixels are the mask area | [Sprite Mask component reference](https://docs.unity3d.com/Manual/sprite/mask/sprite-mask-reference.html) |
| Alpha Cutoff | Minimum alpha counted as part of the mask — lowering it pulls semi-transparent edges into the shape | [Sprite Mask component reference](https://docs.unity3d.com/Manual/sprite/mask/sprite-mask-reference.html) |
| Sprite Sort Point | Center or Pivot, used when distance is the active sort tie-breaker | [Sprite Mask component reference](https://docs.unity3d.com/Manual/sprite/mask/sprite-mask-reference.html) |
| Custom Range | Restricts the mask to a band of Sorting Layers instead of every sprite it geometrically overlaps — the scalable way to keep several masks from interfering | [Sprite Mask component reference](https://docs.unity3d.com/Manual/sprite/mask/sprite-mask-reference.html) |
| Front / Back Sorting Layer + Order in Layer | The two boundaries of that band; anything outside is unmasked | [Sprite Mask component reference](https://docs.unity3d.com/Manual/sprite/mask/sprite-mask-reference.html) |
| Rendering Layer Mask | Restricts masking by rendering layer, independently of draw order | [Sprite Mask component reference](https://docs.unity3d.com/Manual/sprite/mask/sprite-mask-reference.html) |

## Opting a renderer in

| Mask Interaction on the target `SpriteRenderer` | Result | Source |
|---|---|---|
| None | Unaffected by every mask — the default, which is why a new mask appears to do nothing until targets are opted in | [Add a sprite mask](https://docs.unity3d.com/Manual/sprite/mask/hide-reveal-parts-sprite-mask.html) |
| Visible Inside Mask | Only the overlapping part renders | [Add a sprite mask](https://docs.unity3d.com/Manual/sprite/mask/hide-reveal-parts-sprite-mask.html) |
| Visible Outside Mask | The overlapping part is hidden | [Add a sprite mask](https://docs.unity3d.com/Manual/sprite/mask/hide-reveal-parts-sprite-mask.html) |

Prefer Custom Range over opting every unrelated sprite out one by one: scoping
one mask is a single edit, while the opt-out approach has to be repeated for
every sprite added to the scene afterwards. Pair it with a
[Sorting Group](sorting-sprites.md) around each mask-and-target set when
several masks must stay independent.
