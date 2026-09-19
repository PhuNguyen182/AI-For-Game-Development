# Tilemap Scripting API — Reads, Batched Writes & Refresh

Source: [Tilemap API](https://docs.unity3d.com/ScriptReference/Tilemaps.Tilemap.html).
Covers: SKILL.md §4 — **"Batch runtime tile edits and keep them out of `Update`"**.

Tile edits are authoring and load-time operations that happen to be callable
at runtime. Each write invalidates render and collider data for the affected
region, so the difference between a batched call and a loop of single writes
is the difference between one invalidation and one per cell.

## Reading

| Member | What it decides | Source |
|---|---|---|
| `cellBounds`, `origin`, `size` | The occupied region in cell coordinates — the bounds any iteration should be driven from rather than a guessed range | [Tilemap API](https://docs.unity3d.com/ScriptReference/Tilemaps.Tilemap.html) |
| `GetTile(Vector3Int)` / `GetTile<T>(Vector3Int)` | The tile at a cell, optionally typed — the generic overload avoids a cast when a custom tile type is expected | [Tilemap.GetTile](https://docs.unity3d.com/ScriptReference/Tilemaps.Tilemap.GetTile.html) |
| `HasTile(Vector3Int)` | Occupancy without fetching the asset — the cheap test for a walkability query | [Tilemap.HasTile](https://docs.unity3d.com/ScriptReference/Tilemaps.Tilemap.HasTile.html) |
| `GetSprite(Vector3Int)` | The sprite actually rendered there, which for a Rule Tile is not the tile's default | [Tilemap.GetSprite](https://docs.unity3d.com/ScriptReference/Tilemaps.Tilemap.GetSprite.html) |
| `tileAnchor`, `color`, `animationFrameRate` | Runtime equivalents of the component fields in [grid-and-tilemap.md](grid-and-tilemap.md) | [Tilemap API](https://docs.unity3d.com/ScriptReference/Tilemaps.Tilemap.html) |

## Writing

| Member | What it decides | Source |
|---|---|---|
| `SetTile(Vector3Int, TileBase)` | One cell — correct for a single event-driven change, wrong inside a loop | [Tilemap.SetTile](https://docs.unity3d.com/ScriptReference/Tilemaps.Tilemap.SetTile.html) |
| `SetTiles(Vector3Int[], TileBase[])` | Many cells in one call, invalidating render and collider data once instead of per cell | [Tilemap.SetTiles](https://docs.unity3d.com/ScriptReference/Tilemaps.Tilemap.SetTiles.html) |
| `BoxFill(...)` / `FloodFill(...)` | A rectangle, or a contiguous matching region, in one operation | [Tilemap.BoxFill](https://docs.unity3d.com/ScriptReference/Tilemaps.Tilemap.BoxFill.html) |
| `SwapTile(TileBase, TileBase)` | Replaces **every** instance of one tile across the whole tilemap — a global operation frequently mistaken for a local one | [Tilemap.SwapTile](https://docs.unity3d.com/ScriptReference/Tilemaps.Tilemap.SwapTile.html) |
| `SetColor(Vector3Int, Color)` | Per-tile tint; requires the tile's Lock Color flag to be clear | [Tilemap.SetColor](https://docs.unity3d.com/ScriptReference/Tilemaps.Tilemap.SetColor.html) |
| `ClearAllTiles()` | Empties the layer — the correct reset before repainting a procedurally generated level | [Tilemap.ClearAllTiles](https://docs.unity3d.com/ScriptReference/Tilemaps.Tilemap.ClearAllTiles.html) |
| `RefreshTile(Vector3Int)` / `RefreshAllTiles()` | Forces render and animation data to re-resolve; `RefreshAllTiles` is a whole-map cost and is rarely what a single change needs | [Tilemap.RefreshTile](https://docs.unity3d.com/ScriptReference/Tilemaps.Tilemap.RefreshTile.html) |

**Critical caveat**: crossing `TilemapCollider2D`'s Maximum Tile Change Count
in one batch converts an incremental collider update into a full rebuild — see
[tilemap-collider-2d.md](tilemap-collider-2d.md). A large procedural repaint
should expect that cost rather than be surprised by it.
