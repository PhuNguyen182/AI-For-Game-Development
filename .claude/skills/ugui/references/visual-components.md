# Visual Components

## Image
Renders a `Sprite` (import the texture as Sprite (2D and UI)).

| Type | Behaviour | Fits |
|---|---|---|
| Simple | Uniform scale | Fixed-size icon |
| Sliced | 9-slice (borders set once on the sprite in the Sprite Editor); only the middle stretches | Resizable panel/button background |
| Tiled | Like Sliced, repeats the centre | Background with constant-scale texture |
| Filled | Reveals from an origin by Fill Method/Origin/Amount | Radial/linear progress or cooldown |

`Set Native Size` works for Simple/Filled only.

## RawImage
Renders a `Texture`: no 9-slice, no atlas. Use only for a non-sprite texture (RenderTexture feed, runtime texture); otherwise `Image`.

## Text (legacy)
Has Best Fit (shrinks font to the rect). New work uses `TMP_Text` ([textmeshpro-core-and-rich-text.md](textmeshpro-core-and-rich-text.md)); tags in [legacy-text-and-rich-text.md](legacy-text-and-rich-text.md).

## Mask vs RectMask2D
| | `Mask` | `RectMask2D` |
|---|---|---|
| Mechanism | Stencil buffer written by the masking Graphic | Rectangular clip, no stencil |
| Shape | Any (the Graphic's alpha) | Rectangle only |
| Cost | Extra draw call; nested masks AND their stencil bits and can force a material variant per depth | No extra draw calls or materials |
| Requires | A `Graphic` on the same GameObject | No `Graphic` |
| Caveat | none documented | Does not mask elements that are not coplanar with it |

Default to `RectMask2D` (e.g. a `ScrollRect` Viewport); `Mask` only for a non-rectangular clip. "Show Mask Graphic" toggles whether the mask Graphic itself renders.

## Effects (Text/Image only)
- **Shadow**: duplicates vertices offset by Effect Distance, tinted by Effect Color; Use Graphic Alpha multiplies the source alpha.
- **Outline**: the same duplication in several directions.
- **Position As UV1**: feeds the offset into UV1 for a custom shader.

Each duplicates every vertex of its Graphic; check many simultaneous instances in the UI Profiler.
