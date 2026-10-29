# Grid, Tilemap, Isometric & Hexagonal

Pages: https://docs.unity3d.com/Manual/tilemaps/grid-reference.html, https://docs.unity3d.com/Manual/tilemaps/work-with-tilemaps/create-tilemap-landing.html

`Grid` owns cell geometry; `Tilemap` is a child holding painted data plus a `TilemapRenderer`. Several `Tilemap` children under one `Grid` are provably cell-aligned.

## Hierarchy

- Hierarchy > 2D Object > Tilemap > <type> creates the Grid plus one Tilemap, Cell Layout implied by the type (Rectangular, Hexagonal, Isometric). Add further Tilemap children per role.
- Window > 2D > Tile Palette, **Active Tilemap** selects the layer painted into; painting into the wrong layer is silent.

| Grid property | Decision |
|---|---|
| Cell Size | World size of a cell; must agree with the palette's value; derived for isometric |
| Cell Gap | Spacing that shifts every tile after the first; rarely wanted |
| Cell Layout | Rectangle, Hexagon, Isometric, Isometric Z as Y (height in one tilemap; plain Isometric needs one tilemap per level) |
| Cell Swizzle | World axes the grid occupies; XYZ is flat 2D default |

| Tilemap property | Decision |
|---|---|
| Animation Frame Rate | Multiplier for every animated tile on the layer |
| Color | Tints the layer; white leaves art untouched |
| Tile Anchor | Tile position in its cell, default (0.5, 0.5, 0); shifts art half a cell when it disagrees with the sprite pivot |
| Orientation | Paint plane (XY, XZ, ...) or Custom offset/rotation/scale |
| Info | Read-only list of tiles/sprites in use; selecting pings the asset |

## Isometric

Cells that do not line up and depth that reads backwards are two independent failures; fix both.

1. Import sprites at Mesh Type Tight, PPU equal to tile pixel width, pivot at the centre of the tile's 3D floor (import work: `unity-2d-sprite`).
2. Palette type Isometric, **Cell Size y = floor height px ÷ tile width px** (32 px floor on a 64 px tile = 0.5). Derive, never round.
3. Isometric vs **Isometric Z as Y**: flat Isometric stacks one tilemap per height; Z as Y encodes height in one tilemap, needed for ramps and multi-level terrain.
4. Match the Grid's Cell Size y to the palette's (two copies of one derived number; usually only one gets updated).
5. Transparency Sort Mode = Custom Axis, axis (0, 1, 0); otherwise depth sorts by camera distance and reads inverted. Set on the 2D Renderer Data (URP) or Project Settings > Graphics > Camera Settings (Built-in). Sprite sorting semantics: `unity-2d-sprite`.

## Hexagonal

| Type | Decision |
|---|---|
| Point Top | Vertex top and bottom; alternating **rows** offset right by half a cell |
| Flat Top | Flat edge top and bottom, **x and y swapped** vs Point Top (Cell Size x governs vertical spacing, y horizontal); alternating **columns** offset downward |

Sprites: rectangular slices work; Sprite Mode Polygon gives a tighter hex silhouette. Palette type (Hexagonal Point Top / Flat Top) must match the Grid's Cell Layout Hexagon.
