# Tilemap Scripting API

Page: https://docs.unity3d.com/ScriptReference/Tilemaps.Tilemap.html

Each write invalidates render and collider data for the affected region; a batched call is one invalidation, a loop of `SetTile` is one per cell. Crossing `TilemapCollider2D` Maximum Tile Change Count in one batch converts the incremental collider update into a full rebuild (large procedural repaints should expect this).

| Member | Note |
|---|---|
| `cellBounds`, `origin`, `size` | Drive iteration from these, not a guessed range |
| `GetTile(Vector3Int)` / `GetTile<T>` | Generic avoids a cast for a custom tile type |
| `HasTile(Vector3Int)` | Cheap occupancy test (walkability) |
| `GetSprite(Vector3Int)` | Sprite actually rendered; for a Rule Tile not the default |
| `tileAnchor`, `color`, `animationFrameRate` | Runtime equivalents of the component fields |
| `SetTile(Vector3Int, TileBase)` | One event-driven change; not for loops |
| `SetTiles(Vector3Int[], TileBase[])` | Many cells, one invalidation |
| `BoxFill(...)` / `FloodFill(...)` | Rectangle / contiguous matching region in one operation |
| `SwapTile(TileBase, TileBase)` | Replaces **every** instance across the tilemap (global, often mistaken for local) |
| `SetColor(Vector3Int, Color)` | Per-tile tint; the tile's Lock Color flag must be clear |
| `ClearAllTiles()` | Reset before repainting a procedural level |
| `RefreshTile(Vector3Int)` / `RefreshAllTiles()` | Re-resolve render/animation data; `RefreshAllTiles` is a whole-map cost |
