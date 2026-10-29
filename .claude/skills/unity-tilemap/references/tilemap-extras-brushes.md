# 2D Tilemap Extras — Brushes & GridInformation

Package `com.unity.2d.tilemap.extras@8.0` (install via Window > Package Manager > Unity Registry). Pages: https://docs.unity3d.com/Packages/com.unity.2d.tilemap.extras@8.0/manual/Brushes.html (and LineBrush.html, RandomBrush.html, GroupBrush.html, GameObjectBrush.html, GridInformation.html there). All four brushes extend `GridBrush` in `UnityEditor.Tilemaps`: editor-only.

## Line Brush

| Member | Decision |
|---|---|
| `fillGaps` | Inserts tiles so a diagonal stays orthogonally connected; matters when the line is a collision surface |
| `lineStart` / `lineStartActive` | Pending start cell; first click sets it, second draws |
| `GetPointsOnLine(Vector2Int, Vector2Int)` | Bresenham cells between two points (with a `fillGaps` overload); reusable by tooling |
| Lock Z Position | Pins tiles to the start tile's Z; keeps a line flat on Isometric Z as Y |

## Random Brush

| Member | Decision |
|---|---|
| `randomTileSets` | Pool; selection is **uniform**, no weighting, so a rare variant needs a Rule Tile or custom brush |
| `randomTileSetSize` | Block per stroke (2×2 paints four cells) |
| `pickRandomTiles` / `addToRandomTiles` | Whether picking from the palette replaces or extends the pool |

## Group Brush

| Member | Decision |
|---|---|
| `gap` | Empty cells allowed before content stops being one group |
| `limit` | Max group extent per axis from the initial cell; stops a pick swallowing a level |

## GameObject Brush

| Property | Decision |
|---|---|
| Game Object | Prefab asset from the Project window, not a scene instance |
| Offset / Anchor / Scale / Orientation | Placement in the cell; Scale defaults to one cell, so set it for oversized prefabs |
| Size | Multi-cell block per stroke |
| Active Tilemap = (Paint on Scene Root) | Parents instances at the Hierarchy root instead of under the Grid (props then do not move with the grid) |

Painted GameObjects are scene objects, not tile data: outside chunk culling (tilemap-renderer.md) and `TilemapCollider2D` generation.

## GridInformation

Per-cell metadata without inventing a tile type.

| Member | Decision |
|---|---|
| `SetPositionProperty(position, name, value)` | Stores `int`, `float`, `double`, `string`, `Color` or `Object` under a key |
| `GetPositionProperty(position, name, defaultValue)` | Typed read with fallback for unwritten cells |
| `ErasePositionProperty(position, name)` | Removes one value |
| `GetAllPositions(name)` | Every cell with a key, no map scan |
| `Reset()` | Clears all |

A store, not a decision-maker: interpreting its metadata as a game rule belongs in `Game.Core.*`.
