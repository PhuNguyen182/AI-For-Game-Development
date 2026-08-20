# 2D Tilemap Extras — Additional Brushes & Grid Information

Sources: https://docs.unity3d.com/Packages/com.unity.2d.tilemap.extras@8.0/manual/index.html, https://docs.unity3d.com/Packages/com.unity.2d.tilemap.extras@8.0/manual/install.html, https://docs.unity3d.com/Packages/com.unity.2d.tilemap.extras@8.0/manual/Brushes.html, https://docs.unity3d.com/Packages/com.unity.2d.tilemap.extras@8.0/manual/LineBrush.html, https://docs.unity3d.com/Packages/com.unity.2d.tilemap.extras@8.0/manual/RandomBrush.html, https://docs.unity3d.com/Packages/com.unity.2d.tilemap.extras@8.0/manual/GroupBrush.html, https://docs.unity3d.com/Packages/com.unity.2d.tilemap.extras@8.0/manual/GameObjectBrush.html, https://docs.unity3d.com/Packages/com.unity.2d.tilemap.extras@8.0/manual/GridInformation.html, `UnityEditor.Tilemaps.LineBrush`/`RandomBrush`/`GroupBrush`/`GameObjectBrush` and `UnityEngine.GridInformation` scripting API

## Package requirement

The Line/Random/Group/GameObject brushes described in [brushes.md](brushes.md) — and Grid Information below — all ship in the separate **2D Tilemap Extras** package (`com.unity.2d.tilemap.extras`), not Unity's core Tilemap module. Install via **Window > Package Manager > Unity Registry > 2D Tilemap Extras** first.

## Line Brush

Paints a straight line of tiles between two clicked points.

1. Tile Palette window > Brush Inspector > set brush = **Line Brush**.
2. Select **Paint with Active Brush**, choose a tile, click once for the start point, click again for the end point.

| Property | Description |
|---|---|
| Fill Gaps | Inserts extra tiles so diagonal segments stay orthogonally connected (no corner-only touching gaps). |
| Line Start | The current line's starting cell; adjustable after the first click. |
| Lock Z Position | Locks all painted tiles to the start tile's Z. |
| Scene View Z Position / Palette Z Position | Manual Z control, only available when Lock Z Position is off. |

Scripting API — `UnityEditor.Tilemaps.LineBrush` (extends `GridBrush`): `lineStart` (`Vector3Int`), `lineStartActive` (`bool`), `fillGaps` (`bool`), `IsMoving`; `Paint(GridLayout, GameObject, Vector3Int)` (first click sets the start, second draws the line); `GetPointsOnLine(Vector2Int, Vector2Int)` / overload with a `fillGaps` bool — enumerates cells between two points via Bresenham's line algorithm; `MoveStart`/`MoveEnd`.

## Random Brush

Paints a randomly-selected tile set from a configured pool on every stroke — **equal chance across the pool, no per-tile probability weighting**.

1. Brush Inspector > set brush = **Random Brush**.
2. Either **Add To Random Tiles** + Pick individual tiles from the palette, or set **Number of Tiles** and drag tiles into the numbered slots directly.
3. **Tile Set Size** controls the painted group's dimensions (e.g. 2×2 paints a 2×2 block per stroke, not a single cell).
4. Paint with Active Brush as usual.

Scripting API — `UnityEditor.Tilemaps.RandomBrush` (extends `GridBrush`): `randomTileSets`, `randomTileChangeDataSets` (the pool of options), `randomTileSetSize` (`Vector3Int`), `pickRandomTiles`, `addToRandomTiles`; `Paint(GridLayout, GameObject, Vector3Int)`, `Pick(GridLayout, GameObject, BoundsInt, Vector3Int)`.

## Group Brush

Picks a whole contiguous group of tiles at once instead of a single tile, based on adjacency.

1. Brush Inspector > set brush = **Group Brush**.
2. Select **Paint with Active Brush**, click a tile — the brush expands the selection to the connected group around it.

| Property | Description |
|---|---|
| Gap | How many empty cells must border a group before Unity stops considering it part of the group. |
| Limit | Maximum group size per axis, in cells beyond the initial position. |
| Lock Z Position | Same semantics as Line Brush. |

Scripting API — `UnityEditor.Tilemaps.GroupBrush` (extends `GridBrush`): `gap` (`Vector3Int`), `limit` (`Vector3Int`); `Pick(GridLayout, GameObject, BoundsInt, Vector3Int)`.

## GameObject Brush

Paints GameObject instances (prefabs) onto the grid instead of `Tile` assets.

1. Brush Inspector > set brush = **GameObject Brush**.
2. Paint in the Scene view — Unity instantiates the assigned GameObject under the active `Grid` per painted cell (or under the Hierarchy root if the Active Tilemap is set to **(Paint on Scene Root)**).

| Property | Description |
|---|---|
| Game Object | The prefab to paint; must be dragged from the Project window (a prefab asset, not a scene instance). |
| Offset | Position offset relative to the cell, e.g. `(0.5, 0.5, 0)`. |
| Scale | Instance scale; default is one tilemap cell. |
| Orientation | Instance rotation. |
| Size | Paints a multi-cell grid of instances (e.g. 2×3) per stroke. |
| Anchor | Where within the cell the instance is positioned; defaults to centered. |

Scripting API — `UnityEditor.Tilemaps.GameObjectBrush` (extends `GridBrush`): `size`, `pivot`, `cells`, `cellCount`, `canChangeZPosition`; `Paint()`, `Erase()`, `BoxFill()`, `BoxErase()`, `SetGameObject()`, `SetOffset()`/`SetScale()`/`SetOrientation()`, `GetCellIndex()`, `Init()`, `Rotate()`, `Flip()`, `MoveStart()`/`MoveEnd()`.

## Grid Information

A `MonoBehaviour` that stores/retrieves arbitrary keyed data at grid positions — useful for metadata a custom Scriptable Tile's `GetTileData` needs to read (e.g. a per-cell terrain-type tag) without encoding it into the tile asset itself.

1. Select the `Grid` GameObject, **Add Component > Grid Information**.
2. Call its API from editor tooling or a custom `TileBase`/`GridBrushBase` script.

| Member | Description |
|---|---|
| `SetPositionProperty(position, name, value)` | Stores a value (`int`, `float`, `double`, `string`, `Color`, or `UnityEngine.Object`) at a cell, keyed by property name. |
| `GetPositionProperty(position, name, defaultValue)` | Reads a stored value, with type-specific overloads and a default fallback. |
| `ErasePositionProperty(position, name)` | Removes one stored value. |
| `GetAllPositions(name)` | Returns every cell position that has a given property name set. |
| `Reset()` | Clears all stored data. |

## Practical guidance

- Confirm the 2D Tilemap Extras package is installed before referencing any brush/component on this page — none of them ship with core Unity.
- Reach for Line/Random/Group/GameObject brushes only when the design genuinely needs that repeated painting behavior; a one-off arrangement is simpler with the plain Default Brush (KISS in `coding-principles.md`), consistent with [brushes.md](brushes.md)'s guidance.
- Grid Information is a data store, not a decision-maker — the interpretation of whatever it holds (e.g. "this terrain type deals damage") still belongs in Shared Core, per `coding-principles.md`'s Shared Core integrity rule; use it to carry authoring-time metadata to the rendering/painting layer, not to encode gameplay rules.
