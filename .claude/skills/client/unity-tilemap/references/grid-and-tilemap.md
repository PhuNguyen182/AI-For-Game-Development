# Grid & Tilemap — Hierarchy, Cell Layout & Painting Flow

Sources: [Tilemaps](https://docs.unity3d.com/Manual/tilemaps/tilemaps.html), [Grid component reference](https://docs.unity3d.com/Manual/tilemaps/grid-reference.html), [Create a Tilemap](https://docs.unity3d.com/Manual/tilemaps/work-with-tilemaps/create-tilemap.html), [Tilemap component reference](https://docs.unity3d.com/Manual/tilemaps/work-with-tilemaps/tilemap-reference.html).
Covers: SKILL.md §4 — **"Settle the Cell Layout before creating anything"**.

`Grid` is the infinite layout guide that owns cell geometry; `Tilemap` is a
child holding painted data and a `TilemapRenderer`. The structural decision
this file exists for: **several `Tilemap` children under one `Grid`** keeps
ground, walls, and decoration provably cell-aligned, whereas separate `Grid`
hierarchies with differing cell sizes drift apart invisibly.

## Creating the hierarchy

| Step | What it decides | Source |
|---|---|---|
| **Hierarchy > 2D Object > Tilemap > <type>** | Creates the `Grid` plus one `Tilemap` child, with the Cell Layout implied by the type chosen — Rectangular, Hexagonal, or Isometric | [Create a Tilemap](https://docs.unity3d.com/Manual/tilemaps/work-with-tilemaps/create-tilemap.html) |
| Add further `Tilemap` children | One layer per role, all sharing the parent's cell geometry — the only way to guarantee alignment between layers | [Create a Tilemap](https://docs.unity3d.com/Manual/tilemaps/work-with-tilemaps/create-tilemap.html) |
| **Window > 2D > Tile Palette**, set Active Tilemap | Which layer painting operations write into; painting into the wrong layer is silent | [Tile Palette](https://docs.unity3d.com/Manual/tilemaps/tile-palettes/tile-palette-editor-reference.html) |

## Grid properties

| Property | What it decides | Source |
|---|---|---|
| Cell Size | The world size of one cell. Must agree with the palette's own value, and for isometric it is derived rather than chosen — see [isometric-hexagonal.md](isometric-hexagonal.md) | [Grid reference](https://docs.unity3d.com/Manual/tilemaps/grid-reference.html) |
| Cell Gap | Spacing between cells, which shifts every tile after the first — rarely wanted outside deliberate lattice art | [Grid reference](https://docs.unity3d.com/Manual/tilemaps/grid-reference.html) |
| Cell Layout | **Rectangle**, **Hexagon**, **Isometric**, or **Isometric Z as Y**. Z as Y encodes height in a single tilemap; plain Isometric needs one tilemap per level | [Grid reference](https://docs.unity3d.com/Manual/tilemaps/grid-reference.html) |
| Cell Swizzle | Which world axes the grid occupies — XYZ is the flat 2D default, and the others place a tile grid into a 3D scene | [Grid reference](https://docs.unity3d.com/Manual/tilemaps/grid-reference.html) |

## Tilemap properties

| Property | What it decides | Source |
|---|---|---|
| Animation Frame Rate | Multiplier over the base rate for every animated tile on this layer — the single dial that speeds up or slows a whole layer's animation | [Tilemap reference](https://docs.unity3d.com/Manual/tilemaps/work-with-tilemaps/tilemap-reference.html) |
| Color | Tints every tile the layer renders; white leaves art untouched | [Tilemap reference](https://docs.unity3d.com/Manual/tilemaps/work-with-tilemaps/tilemap-reference.html) |
| Tile Anchor | Tile position within its cell, default (0.5, 0.5, 0) — the setting that shifts art half a cell when it disagrees with the sprite's pivot | [Tilemap reference](https://docs.unity3d.com/Manual/tilemaps/work-with-tilemaps/tilemap-reference.html) |
| Orientation | Which plane tiles paint into — XY, XZ, and the rest, or Custom with explicit offset, rotation, and scale | [Tilemap reference](https://docs.unity3d.com/Manual/tilemaps/work-with-tilemaps/tilemap-reference.html) |
| Info | Read-only list of tiles and sprites in use; selecting one pings it in the Project window, which is how an unexpected tile is traced back to its asset | [Tilemap reference](https://docs.unity3d.com/Manual/tilemaps/work-with-tilemaps/tilemap-reference.html) |
