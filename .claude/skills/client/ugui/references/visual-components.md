# Visual Components — Image, RawImage, Text, Mask, Effects

Source: [Visual Components](https://docs.unity3d.com/Packages/com.unity.ugui@2.6/manual/UIVisualComponents.html), [Mask](https://docs.unity3d.com/Packages/com.unity.ugui@2.6/manual/script-Mask.html), [RectMask2D](https://docs.unity3d.com/Packages/com.unity.ugui@2.6/manual/script-RectMask2D.html), [UI Effects](https://docs.unity3d.com/Packages/com.unity.ugui@2.6/manual/comp-UIEffects.html).
Covers: SKILL.md §4 — "Pick the Image Type deliberately, never leave it at Simple by habit", "Reach for RectMask2D before Mask".

## Image

`Image` renders a `Sprite`. Import the source texture as **Sprite (2D and
UI)** so it is eligible.

| Image Type | Behavior | Fits |
|---|---|---|
| **Simple** | Scales the whole sprite uniformly | A plain icon or picture with no resizing needs |
| **Sliced** | 9-slice division (via the Sprite Editor's border handles) — resizing stretches only the middle, corners stay undistorted | A resizable panel/button background |
| **Tiled** | Like Sliced, but repeats (tiles) the center region instead of stretching it | A resizable background that must keep a constant-scale repeating texture rather than stretch |
| **Filled** | Renders like Simple but reveals the sprite from an origin, by a chosen Fill Method/Origin/Amount | A radial or linear progress/cooldown indicator |

`Set Native Size` (Simple/Filled only) resets the RectTransform to the
sprite's native pixel size. 9-slicing itself is configured once, on the
sprite, in the Sprite Editor — not per `Image` instance.

## RawImage

Renders a `Texture` directly rather than a `Sprite` — no 9-slicing, no
atlas participation. Reach for `Image` in the large majority of cases per
the Manual's own guidance; use `RawImage` only for a texture that
genuinely isn't a sprite (a RenderTexture feed, a runtime-generated
texture without sprite metadata).

## Text (legacy)

The non-TMP `Text` component: a font, style, alignment, rich text support
(see [legacy-text-and-rich-text.md](legacy-text-and-rich-text.md)),
horizontal/vertical overflow handling, and a **Best Fit** option that
shrinks the font size to fit the available rect. Prefer TextMeshPro's
`TMP_Text` (see [textmeshpro-core-and-rich-text.md](textmeshpro-core-and-rich-text.md))
for new work — legacy `Text` remains for compatibility with existing
screens, not as the default choice for something new.

## Mask vs RectMask2D

Both restrict child visibility to a shape, but they are not interchangeable:

| | `Mask` | `RectMask2D` |
|---|---|---|
| Mechanism | GPU stencil buffer — the masking Graphic writes a bit, descendants only render where the stencil test passes | Pure rectangular clip, no stencil buffer at all |
| Shape | Any shape the masking Graphic's alpha describes (a circular sprite, etc.) | Rectangle only |
| Draw calls / material changes | Costs an extra draw call and can force a material variant per nesting depth (nested Masks AND their stencil bits together) | No extra draw calls, no material changes |
| Requires | Must sit on the same GameObject as a `Graphic` (the mask shape) | No `Graphic` required at all |
| Coplanarity | Not documented as a constraint | Will not properly mask elements that are not coplanar with it |

**Default to `RectMask2D`** for the extremely common case of clipping a
scroll view/grid to a rectangular viewport — it is cheaper on every axis
that matters (draw calls, materials, stencil buffer) and `ScrollRect`'s own
Viewport is exactly this rectangular case. Reach for `Mask` only when the
clip shape is genuinely non-rectangular (a circular portrait frame, a
custom-shaped reveal).

`Mask`'s "Show Mask Graphic" toggle controls whether the masking Graphic
itself renders (with its own alpha) over the masked children, or is
invisible and purely functional.

## Effects — Shadow, Outline, Position As UV1

Add simple effects to a `Text` or `Image` Graphic on the same GameObject:

- **Shadow** — duplicates the Graphic's vertices offset by Effect Distance,
  tinted by Effect Color; Use Graphic Alpha multiplies the shadow's alpha by
  the source Graphic's own alpha.
- **Outline** — the same duplication technique applied in multiple
  directions to fake an outline.
- **Position As UV1** — feeds the effect's offset into the UV1 channel
  instead of the position, for a custom shader to consume.

Both Shadow and Outline duplicate every vertex of the Graphic they're
attached to — each is a real (if usually small) added draw/fill cost per
instance; stacking several effect components on many simultaneously
visible elements is the kind of thing to check in the UI Profiler
(per [profiling-performance-and-howtos.md](profiling-performance-and-howtos.md))
before assuming it's free.
