# 2D Tilemap Extras — Line, Random, Group & GameObject Brushes, GridInformation

Sources: [Extras Brushes](https://docs.unity3d.com/Packages/com.unity.2d.tilemap.extras@8.0/manual/Brushes.html), [Line Brush](https://docs.unity3d.com/Packages/com.unity.2d.tilemap.extras@8.0/manual/LineBrush.html), [Random Brush](https://docs.unity3d.com/Packages/com.unity.2d.tilemap.extras@8.0/manual/RandomBrush.html), [Group Brush](https://docs.unity3d.com/Packages/com.unity.2d.tilemap.extras@8.0/manual/GroupBrush.html), [GameObject Brush](https://docs.unity3d.com/Packages/com.unity.2d.tilemap.extras@8.0/manual/GameObjectBrush.html), [Grid Information](https://docs.unity3d.com/Packages/com.unity.2d.tilemap.extras@8.0/manual/GridInformation.html).
Covers: SKILL.md §4 — **"Check the 2D Tilemap Extras package before writing anything custom"**.

Everything here ships in `com.unity.2d.tilemap.extras@8.0` and must be
installed from **Window > Package Manager > Unity Registry** before any of it
can be referenced. All four brushes extend `GridBrush` and live in
`UnityEditor.Tilemaps`, so they are editor-only.

## Line Brush

| Member | What it decides | Source |
|---|---|---|
| Fill Gaps (`fillGaps`) | Inserts extra tiles so a diagonal run stays orthogonally connected instead of touching only at corners — which matters when the line is also a collision surface | [Line Brush](https://docs.unity3d.com/Packages/com.unity.2d.tilemap.extras@8.0/manual/LineBrush.html) |
| `lineStart` / `lineStartActive` | The pending start cell and whether one is set; the first click sets it, the second draws | [Line Brush](https://docs.unity3d.com/Packages/com.unity.2d.tilemap.extras@8.0/manual/LineBrush.html) |
| `GetPointsOnLine(Vector2Int, Vector2Int)` | Enumerates the cells between two points by Bresenham's algorithm, with a `fillGaps` overload — reusable by tooling that needs the same cell set | [Line Brush](https://docs.unity3d.com/Packages/com.unity.2d.tilemap.extras@8.0/manual/LineBrush.html) |
| Lock Z Position | Pins painted tiles to the start tile's Z, which is what keeps a line flat on an Isometric Z as Y map | [Line Brush](https://docs.unity3d.com/Packages/com.unity.2d.tilemap.extras@8.0/manual/LineBrush.html) |

## Random Brush

| Member | What it decides | Source |
|---|---|---|
| `randomTileSets` | The pool painted from. Selection is **uniform** — there is no per-tile weighting, so a deliberately rare variant needs a Rule Tile or custom brush instead | [Random Brush](https://docs.unity3d.com/Packages/com.unity.2d.tilemap.extras@8.0/manual/RandomBrush.html) |
| `randomTileSetSize` | The block painted per stroke — 2×2 paints four cells at once, not one | [Random Brush](https://docs.unity3d.com/Packages/com.unity.2d.tilemap.extras@8.0/manual/RandomBrush.html) |
| `pickRandomTiles` / `addToRandomTiles` | Whether picking from the palette replaces or extends the pool | [Random Brush](https://docs.unity3d.com/Packages/com.unity.2d.tilemap.extras@8.0/manual/RandomBrush.html) |

## Group Brush

| Member | What it decides | Source |
|---|---|---|
| `gap` | How many empty cells must separate content before the brush stops treating it as one group — the dial that decides whether two nearby clusters pick as one | [Group Brush](https://docs.unity3d.com/Packages/com.unity.2d.tilemap.extras@8.0/manual/GroupBrush.html) |
| `limit` | Maximum group extent per axis from the initial cell, which is what stops a pick swallowing a whole level | [Group Brush](https://docs.unity3d.com/Packages/com.unity.2d.tilemap.extras@8.0/manual/GroupBrush.html) |

## GameObject Brush

| Property | What it decides | Source |
|---|---|---|
| Game Object | The prefab painted; it must be a Project-window prefab asset, not a scene instance | [GameObject Brush](https://docs.unity3d.com/Packages/com.unity.2d.tilemap.extras@8.0/manual/GameObjectBrush.html) |
| Offset / Anchor / Scale / Orientation | Placement within the cell, instance scale, and rotation — Scale defaults to one cell, so oversized prefabs need it set deliberately | [GameObject Brush](https://docs.unity3d.com/Packages/com.unity.2d.tilemap.extras@8.0/manual/GameObjectBrush.html) |
| Size | Paints a multi-cell block of instances per stroke | [GameObject Brush](https://docs.unity3d.com/Packages/com.unity.2d.tilemap.extras@8.0/manual/GameObjectBrush.html) |
| Active Tilemap = (Paint on Scene Root) | Parents instances at the Hierarchy root instead of under the `Grid` — the difference between props that move with the grid and props that do not | [GameObject Brush](https://docs.unity3d.com/Packages/com.unity.2d.tilemap.extras@8.0/manual/GameObjectBrush.html) |

Painted GameObjects are scene objects, not tile data, so they fall outside the
chunk culling described in [tilemap-renderer.md](tilemap-renderer.md) and
outside `TilemapCollider2D`'s generation.

## Grid Information

| Member | What it decides | Source |
|---|---|---|
| `SetPositionProperty(position, name, value)` | Stores an `int`, `float`, `double`, `string`, `Color`, or `Object` at a cell under a named key — per-cell metadata without inventing a tile type to carry it | [Grid Information](https://docs.unity3d.com/Packages/com.unity.2d.tilemap.extras@8.0/manual/GridInformation.html) |
| `GetPositionProperty(position, name, defaultValue)` | Typed read with a fallback, so a cell that was never written behaves predictably | [Grid Information](https://docs.unity3d.com/Packages/com.unity.2d.tilemap.extras@8.0/manual/GridInformation.html) |
| `ErasePositionProperty(position, name)` | Removes one stored value | [Grid Information](https://docs.unity3d.com/Packages/com.unity.2d.tilemap.extras@8.0/manual/GridInformation.html) |
| `GetAllPositions(name)` | Every cell carrying a given key — how tooling enumerates tagged cells without scanning the map | [Grid Information](https://docs.unity3d.com/Packages/com.unity.2d.tilemap.extras@8.0/manual/GridInformation.html) |
| `Reset()` | Clears all stored data | [Grid Information](https://docs.unity3d.com/Packages/com.unity.2d.tilemap.extras@8.0/manual/GridInformation.html) |

**Critical caveat**: `GridInformation` is a store, not a decision-maker.
Carrying authoring metadata to the painting layer is its purpose; interpreting
that metadata as a game rule belongs in `Game.Core.*`, per
`coding-principles.md`'s Shared Core integrity section.
