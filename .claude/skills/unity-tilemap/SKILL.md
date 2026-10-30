---
name: unity-tilemap
description: "Tilemaps: Grid layouts (rect, hex, isometric Z as Y), Tile Palette, Rule/Auto/Animated Tile, brushes, TilemapRenderer chunk mode, TilemapCollider2D + CompositeCollider2D, Tilemap API. Use for tile-based 2D levels."
user-invocable: false
---

# Unity Tilemap

Not for: sprite import and atlasing (`unity-2d-sprite`), bodies and joints (`unity-2d-physics`), spline geometry (`unity-2d-spriteshape`), `Light2D` (`unity-urp-rendering`), level-generation rules (`csharp-engineer`, Shared Core).
Docs: https://docs.unity3d.com/Manual/tilemaps/tilemaps.html — core Manual unversioned, so confirm defaults against the project's Editor. Extras pinned to https://docs.unity3d.com/Packages/com.unity.2d.tilemap.extras@8.0/manual/index.html (`com.unity.2d.tilemap.extras@8.0`); not core Unity, so confirm it is installed before using any Rule Tile, Auto Tile, Animated Tile or Line/Random/Group/GameObject brush.

| Reference | Read when |
|---|---|
| [grid-and-tilemap.md](references/grid-and-tilemap.md) | Setting up the Grid/Tilemap hierarchy, painting lands misaligned, or building an isometric or hexagonal grid |
| [tile-palette-and-tiles.md](references/tile-palette-and-tiles.md) | Building a palette, source art edits do not propagate, setting `Tile` fields, or saving a Brush Pick |
| [tilemap-renderer.md](references/tilemap-renderer.md) | Tiles sort wrongly against sprites, or pop in at chunk edges |
| [tilemap-collider-2d.md](references/tilemap-collider-2d.md) | Adding collision to a painted level |
| [scripting-api.md](references/scripting-api.md) | Changing tiles from code |
| [tilemap-extras-tiles.md](references/tilemap-extras-tiles.md) | Auto-tiling, terrain blending, animated tiles, or a Rule Tile subclass |
| [tilemap-extras-brushes.md](references/tilemap-extras-brushes.md) | Line/Random/Group/GameObject brushes, or per-cell metadata (`GridInformation`) |
| [custom-tiles-and-brushes.md](references/custom-tiles-and-brushes.md) | No built-in or Extras tile or brush fits |

## Steps
1. **Settle the Cell Layout before creating anything** — Rectangle, Hexagon, Isometric or Isometric Z as Y must match between the `Grid` and every palette painted into it; a mismatch paints to the wrong cells with no error. One `Grid` with several `Tilemap` children keeps layers cell-aligned; separate Grids with different cell sizes are the usual misalignment cause.
2. **Create the palette through the Tile Set Importer when the art will change** — drag-in tiles are not linked back to the texture, so later art edits silently fail to propagate. Drag-in only for a settled, final palette.
3. **Set each `Tile` Collider Type to the cheapest shape that plays correctly** — Grid when the silhouette matches its cell, Sprite only where the outline differs (only as good as the sprite's authored physics shape, `unity-2d-sprite`).
4. **Derive isometric Cell Size y from the sprite**: floor height px ÷ tile width px. Hexagonal Flat Top swaps which axis governs which spacing, so a Point Top value is wrong by construction.
5. **Set the isometric sort axis before judging depth** — Transparency Sort Mode Custom Axis (0, 1, 0), on the 2D Renderer Data under URP or Project Settings > Graphics > Camera Settings on Built-in.
6. **Keep `TilemapRenderer` on Chunk mode unless tiles must interleave with other sprites** (Individual gives up batching). Set Detect Chunk Culling Bounds to Manual when tiles carry oversized sprites or GameObject-brush content.
7. **Pair `TilemapCollider2D` with a `CompositeCollider2D` for terrain** (plus a Static `Rigidbody2D`); Composite Operation/Order do nothing without that component. Hand the body and material to `unity-2d-physics`.
8. **Check Tilemap Extras before writing custom code**: Rule Tile, Auto Tile, Animated Tile and the extra brushes cover most needs. Rule Tile when neighbour conditions are explicit; Auto Tile when art arrives as a masked layout sheet. Order Rule Tile rules most common first (first match wins). Confirm `com.unity.2d.tilemap.extras` is installed first.
9. **Write a custom `TileBase` or `GridBrushBase` only when nothing built-in or Extras fits**; they become dropdown-selectable assets, so name them clearly.
10. **Batch runtime tile edits and keep them out of `Update`** — `SetTiles`/`BoxFill`/`FloodFill` on an event. Exceeding Maximum Tile Change Count turns an incremental collider update into a full rebuild.
11. **Keep layout meaning out of this layer** — Core decides which tile a generator or destruction rule produces; components here only paint, render and collide it. `GridInformation` carries authoring metadata but never interprets it; `GetTileData` and brushes must not decide gameplay state (they run at edit time too).
12. **Misalignment that could be Cell Size, Grid type or pivot** → name the assumed cause before editing shared palette assets (every scene painted from it is affected).

## Never
- Expect a drag-in palette to track its source art.
- Reuse a Point Top hexagonal Cell Size on a Flat Top grid, or set isometric Cell Size y by eye (re-derive when tile art dimensions change).
- Leave chunk culling Auto with oversized sprites or painted GameObjects.
- Use Individual mode for depth that Sorting Layers already express.
- Assume Random Brush weights tiles — its pool is uniform.
- Use `SwapTile` to change one cell — it replaces every instance of that tile across the tilemap.

## Output
```
## Tilemap Work — <level/feature>
- Layout: Cell Layout, Cell Size x,y, Gap, Swizzle; Tilemap layers and purpose
- Palette: creation path and why, Grid type match confirmed
- Tiles: Collider Type(s) and rationale, GameObject to Instantiate
- Painting: brushes, Brush Picks, Extras installed
- Renderer: Mode, sorting, mask interaction, chunk culling Auto/Manual + bound
- Collision: TilemapCollider2D, CompositeCollider2D, Extrusion Factor, Delaunay
- Isometric/Hex: Cell Size y derivation, sort axis, Point Top vs Flat Top
- Extras / custom: types used, or why custom was needed
- Known limitations: <...>
```

## Example
- "Write a custom TileBase that picks the wall sprite from its neighbours" → declined as new code: that is Rule Tile (3×3 match / no-match / don't-care conditions, in Extras). Installed the package and ordered the rules most common first; a `RuleTile<T>` subclass is justified only for a neighbour condition the built-ins cannot express (custom neighbour IDs start at 3).
