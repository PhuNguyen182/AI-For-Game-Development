# Tilemap Scripting API Surface

Sources: `UnityEngine.Tilemaps.Tilemap` scripting API

## `Tilemap` — key properties

| Member | Description |
|---|---|
| `cellBounds` | Tilemap's bounds, in cell coordinates. |
| `origin` | Tilemap's origin, in cell coordinates. |
| `size` | Tilemap's size, in cells. |
| `tileAnchor` | Script-side equivalent of the Tile Anchor Inspector field. |
| `color` | Script-side equivalent of the Color Inspector field. |
| `animationFrameRate` | Script-side equivalent of Animation Frame Rate. |

## `Tilemap` — key methods

| Member | Description |
|---|---|
| `SetTile(Vector3Int position, TileBase tile)` | Places a tile at one cell. |
| `SetTiles(Vector3Int[] positions, TileBase[] tiles)` | Places multiple tiles in one batched call. |
| `GetTile(Vector3Int position)` / `GetTile<T>(Vector3Int position)` | Reads the tile at a cell. |
| `HasTile(Vector3Int position)` | Whether a cell is occupied. |
| `GetSprite(Vector3Int position)` | Reads the rendered sprite at a cell. |
| `SetColor(Vector3Int position, Color color)` | Tints a single tile. |
| `SwapTile(TileBase from, TileBase to)` | Replaces every instance of one tile with another across the whole tilemap. |
| `BoxFill(Vector3Int position, TileBase tile, int startX, int startY, int endX, int endY)` | Fills a rectangular region with one tile. |
| `FloodFill(Vector3Int position, TileBase tile)` | Fills a contiguous region starting from a cell. |
| `ClearAllTiles()` | Removes every tile. |
| `RefreshTile(Vector3Int position)` / `RefreshAllTiles()` | Forces render/animation data to re-resolve for one tile / every tile. |

## Practical guidance

- Prefer `SetTiles`/`BoxFill`/`FloodFill` over a hand-rolled loop of individual `SetTile` calls when placing more than a handful of cells at once — one batched call avoids redundant per-call collider/render invalidation, consistent with `performance-and-algorithms.md`'s hardware-friendly-execution principle.
- Never call `SetTile`/`RefreshTile` from a per-frame hot path (`Update`) for static level geometry — tilemap edits are an authoring/level-load-time operation, not a per-frame one; a runtime tile change (e.g. a destructible wall) should still be an event-driven call, not a polled one.
- The decision of *which* tile goes where in response to gameplay state (destructible terrain, procedural generation) belongs in Shared Core; this API surface only carries out the placement Shared Core already decided, per `coding-principles.md`'s Shared Core integrity rule.
