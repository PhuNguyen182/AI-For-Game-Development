# Isometric & Hexagonal Tilemaps — Cell Maths, Height & Sort Axis

Sources: [Isometric Tilemaps](https://docs.unity3d.com/Manual/tilemaps/work-with-tilemaps/isometric-tilemaps/isometric-tilemap-landing.html), [Create an Isometric Tilemap](https://docs.unity3d.com/Manual/tilemaps/work-with-tilemaps/isometric-tilemaps/create-isometric-tilemap.html), [Isometric Tilemap Renderer modes](https://docs.unity3d.com/Manual/tilemaps/work-with-tilemaps/isometric-tilemaps/renderer/tilemap-renderer-isometric-modes.html), [Hexagonal Tilemaps](https://docs.unity3d.com/Manual/tilemaps/work-with-tilemaps/hexagonal-tilemaps/hexagonal-tilemap-landing.html).
Covers: SKILL.md §4 — **"Derive isometric Cell Size y from the sprite, never by eye"**, **"Set the isometric sort axis before judging any depth problem"**.

Non-rectangular grids fail in two independent ways that look like one: cells
that do not line up, and depth that reads backwards. The first is a number
derived from the sprite; the second is a camera-side sort setting. Fixing
either alone leaves the map looking broken.

## Isometric setup

| Step | What it decides | Source |
|---|---|---|
| Import sprites at Mesh Type Tight, PPU equal to the tile's pixel width, pivot at the centre of the tile's 3D floor | The pivot is what makes a tile sit on its cell rather than beside it; the import work itself belongs to `unity-2d-sprite` | [Create an Isometric Tilemap](https://docs.unity3d.com/Manual/tilemaps/work-with-tilemaps/isometric-tilemaps/create-isometric-tilemap.html) |
| Palette type Isometric, **Cell Size y = floor height in px ÷ tile width in px** | The single most common cause of a grid that will not line up. A 32 px floor on a 64 px tile gives 0.5 — derive it, never round it | [Create an Isometric Tilemap](https://docs.unity3d.com/Manual/tilemaps/work-with-tilemaps/isometric-tilemaps/create-isometric-tilemap.html) |
| Choose Isometric or **Isometric Z as Y** | Flat Isometric needs one tilemap stacked per height level; Z as Y encodes height inside a single tilemap, which is what continuous ramps and multi-level terrain need | [Isometric Tilemaps](https://docs.unity3d.com/Manual/tilemaps/work-with-tilemaps/isometric-tilemaps/isometric-tilemap-landing.html) |
| Match the `Grid`'s Cell Size y to the palette's | Two independent copies of the same derived number, and only one of them is usually updated | [Create an Isometric Tilemap](https://docs.unity3d.com/Manual/tilemaps/work-with-tilemaps/isometric-tilemaps/create-isometric-tilemap.html) |
| Transparency Sort Mode = Custom Axis, axis (0, 1, 0) | Without it, depth sorts by camera distance and reads inverted for an isometric camera. Set it on the 2D Renderer Data under URP, or under Project Settings > Graphics > Camera Settings for the Built-in pipeline | [Create an Isometric Tilemap](https://docs.unity3d.com/Manual/tilemaps/work-with-tilemaps/isometric-tilemaps/create-isometric-tilemap.html) |

## Hexagonal layouts

| Type | What it decides | Source |
|---|---|---|
| Point Top | Vertex at top and bottom; alternating **rows** offset right by half a cell | [Hexagonal Tilemaps](https://docs.unity3d.com/Manual/tilemaps/work-with-tilemaps/hexagonal-tilemaps/hexagonal-tilemap-landing.html) |
| Flat Top | Flat edge at top and bottom, with **x and y swapped** relative to Point Top: Cell Size x governs vertical spacing and y governs horizontal, and alternating **columns** offset downward | [Hexagonal Tilemaps](https://docs.unity3d.com/Manual/tilemaps/work-with-tilemaps/hexagonal-tilemaps/hexagonal-tilemap-landing.html) |
| Sprite import | Rectangular slices work; Sprite Mode Polygon gives a tighter hex silhouette where the tile's own shape matters | [Hexagonal Tilemaps](https://docs.unity3d.com/Manual/tilemaps/work-with-tilemaps/hexagonal-tilemaps/hexagonal-tilemap-landing.html) |
| Palette and `Grid` must agree | Palette type Hexagonal Point Top or Flat Top against `Grid` Cell Layout Hexagon | [Hexagonal Tilemaps](https://docs.unity3d.com/Manual/tilemaps/work-with-tilemaps/hexagonal-tilemaps/hexagonal-tilemap-landing.html) |

**Critical caveat**: a Cell Size copied from a Point Top project into a Flat
Top one is wrong by construction, because the axes govern the opposite
spacings. The same applies in reverse.
