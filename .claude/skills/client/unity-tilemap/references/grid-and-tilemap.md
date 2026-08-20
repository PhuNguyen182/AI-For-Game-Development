# Grid & Tilemap Components

Sources: https://docs.unity3d.com/Manual/tilemaps/tilemaps.html, https://docs.unity3d.com/Manual/tilemaps/grid-reference.html, https://docs.unity3d.com/Manual/tilemaps/work-with-tilemaps/create-tilemap-landing.html, https://docs.unity3d.com/Manual/tilemaps/work-with-tilemaps/create-tilemap.html, https://docs.unity3d.com/Manual/tilemaps/work-with-tilemaps/tilemap-reference.html

## Creating a Tilemap in the scene

1. Confirm the 2D Sprite package is installed (needed for tile art).
2. **Hierarchy > right-click > 2D Object > Tilemap**, then pick the tilemap type matching the target Tile Palette (**Rectangular** is the default; **Hexagonal**/**Isometric** for those layouts — see [isometric-hexagonal.md](isometric-hexagonal.md)).
3. This creates a **Grid** GameObject (an "infinite layout guide" — the cell-layout authority) with a child **Tilemap** GameObject (holds the actual painted tile data plus `TilemapRenderer`). Multiple `Tilemap` children can share one `Grid` — a common pattern for separate ground/wall/decoration layers that must stay cell-aligned with each other.

## Painting tiles

1. **Window > 2D > Tile Palette** to open the Tile Palette window (see [tile-palette-and-tiles.md](tile-palette-and-tiles.md) for populating it).
2. Set the window's **Active Tilemap** dropdown to the target `Tilemap`.
3. Select the **Paint with Active Brush** tool.
4. Pick tile(s) from the palette (click, drag-select a block, or Ctrl/Cmd-pick straight from the Scene view), then click/drag in the Scene view to paint.
5. Use **Box Fill**, **Flood Fill**, **Eraser**, **Move**, **Rotate**, **Flip** for the rest of the authoring workflow — see [brushes.md](brushes.md) for the full toolbar.

## Grid component properties

| Property | Description |
|---|---|
| Cell Size | Size of each grid cell. |
| Cell Gap | Gap between cells. |
| Cell Layout | **Rectangle**, **Hexagon**, **Isometric**, or **Isometric Z as Y** — see [isometric-hexagonal.md](isometric-hexagonal.md) for the non-rectangular layouts. |
| Cell Swizzle | Grid orientation in 3D space: **XYZ** (default, flat facing the 2D camera), **XZY**, **YXZ**, **YZX**, **ZXY**, **ZYX**. |

## Tilemap component properties

| Property | Description |
|---|---|
| Animation Frame Rate | Multiplier on the base frame rate for all tile animations on this `Tilemap`. |
| Color | Tints every sprite the tilemap renders; white = no tint. |
| Tile Anchor | Position of tiles relative to a cell's bottom-left, default (0.5, 0.5, 0). |
| Orientation | Plane the tiles paint into — **XY**, **XZ**, **YX**, **YZ**, **ZX**, **ZY**, or **Custom**. |
| Offset / Rotation / Scale | Relative transform of the tilemap (Custom orientation only). |
| Info | Read-only list of tiles/sprites the tilemap contains; selecting one highlights it in the Project window. |

## Practical guidance

- Keep gameplay-relevant tile layouts (which tile type occupies which cell, procedurally generated level data) as data resolved in Shared Core when the layout is gameplay-rule-driven (e.g. a seeded dungeon generator); this skill's `Tilemap`/`Grid` components only render/store whatever layout was decided, per `coding-principles.md`'s Shared Core integrity rule.
- Don't add a `Grid`/`Tilemap` per tiny decorative prop set if a single shared `Grid` with multiple `Tilemap` layers already expresses the requirement — extra `Grid` hierarchies with mismatched cell sizes are a common source of misaligned painting.
