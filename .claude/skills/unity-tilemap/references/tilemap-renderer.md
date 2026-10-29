# Tilemap Renderer

Pages: https://docs.unity3d.com/Manual/tilemaps/work-with-tilemaps/tilemap-renderer-reference.html, https://docs.unity3d.com/ScriptReference/Tilemaps.TilemapRenderer.html

Sorting Layer, Order in Layer and Mask Interaction work as on a `SpriteRenderer` (`unity-2d-sprite`). Derives from `Renderer`, so the usual material/bounds/shadow surface applies. Material `Sprite-Lit-Default` under URP; changing it is `shader-authoring`'s. Rendering Layer Mask is for `Light2D` filtering (`unity-urp-rendering`).

| Property (script name) | Decision |
|---|---|
| Mode (`mode`) | **Chunk** (default) batches per region; **Individual** renders each tile so tiles depth-sort against other sprites, giving up batching; **SRP Batch** uses the SRP Batcher |
| Sort Order (`sortOrder`) | Corner tiles sort from within a chunk (Bottom Left default); decides which of two overlapping tiles draws in front |
| Detect Chunk Culling Bounds (`detectChunkCullingBounds`) | **Auto** estimates from sprite bounds; **Manual** required for oversized sprites or painted GameObjects, else content pops in at chunk edges |
| Chunk Culling Bounds (`chunkCullingBounds`) | Extra boundary distance in units, Manual only |
| `chunkSize` | Tiles per chunk; larger batches more and culls coarser |
| `maxChunkCount`, `maxFrameAge` | Chunks cached and unused frames kept; memory vs rebuild dial for large scrolling maps |
| `GetShaderUserValue()` / `SetShaderUserValue()` | Per-tile shader data without a material per tile |
