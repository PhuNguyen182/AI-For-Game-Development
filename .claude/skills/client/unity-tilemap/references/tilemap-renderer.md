# Tilemap Renderer — Mode, Sorting, Masking & Chunk Culling

Sources: [Tilemap Renderer component reference](https://docs.unity3d.com/Manual/tilemaps/work-with-tilemaps/tilemap-renderer-reference.html), [TilemapRenderer API](https://docs.unity3d.com/ScriptReference/Tilemaps.TilemapRenderer.html).
Covers: SKILL.md §4 — **"Keep `TilemapRenderer` on Chunk mode unless tiles must interleave with other sprites"**.

`TilemapRenderer` draws a layer's tiles and decides how they batch. The
central trade-off is Mode: Chunk batches whole regions and cannot interleave
individual tiles with other sprites, while Individual can, at the cost of that
batching. Sorting Layer and Mask Interaction carry the same semantics as any
sprite renderer, which `unity-2d-sprite` documents.

## Inspector

| Property | What it decides | Source |
|---|---|---|
| Mode | **Chunk** batches per region and is the default; **Individual** renders each tile separately so tiles can depth-sort against other sprites, giving up the batch to do it; **SRP Batch** routes through the Scriptable Render Pipeline Batcher | [Tilemap Renderer reference](https://docs.unity3d.com/Manual/tilemaps/work-with-tilemaps/tilemap-renderer-reference.html) |
| Sort Order | Which corner tiles sort from within a chunk — Bottom Left by default; it decides which of two overlapping tiles in the same chunk draws in front | [Tilemap Renderer reference](https://docs.unity3d.com/Manual/tilemaps/work-with-tilemaps/tilemap-renderer-reference.html) |
| Detect Chunk Culling Bounds | **Auto** estimates from sprite bounds; **Manual** is required when tiles carry oversized sprites or painted GameObjects, because an underestimate pops content in at chunk edges | [Tilemap Renderer reference](https://docs.unity3d.com/Manual/tilemaps/work-with-tilemaps/tilemap-renderer-reference.html) |
| Chunk Culling Bounds | The extra boundary distance in units, Manual mode only | [Tilemap Renderer reference](https://docs.unity3d.com/Manual/tilemaps/work-with-tilemaps/tilemap-renderer-reference.html) |
| Mask Interaction | None, Visible Inside Mask, or Visible Outside Mask — same semantics as a `SpriteRenderer`, documented by `unity-2d-sprite` | [Tilemap Renderer reference](https://docs.unity3d.com/Manual/tilemaps/work-with-tilemaps/tilemap-renderer-reference.html) |
| Material | `Sprite-Lit-Default` under URP; changing it is a shader decision owned by `shader-authoring` | [Tilemap Renderer reference](https://docs.unity3d.com/Manual/tilemaps/work-with-tilemaps/tilemap-renderer-reference.html) |
| Sorting Layer / Order in Layer | The layer's position in the 2D sort chain, whose full semantics `unity-2d-sprite` documents | [Tilemap Renderer reference](https://docs.unity3d.com/Manual/tilemaps/work-with-tilemaps/tilemap-renderer-reference.html) |
| Rendering Layer Mask | Which rendering layers apply, e.g. for `Light2D` filtering owned by `unity-urp-rendering` | [Tilemap Renderer reference](https://docs.unity3d.com/Manual/tilemaps/work-with-tilemaps/tilemap-renderer-reference.html) |

## Scripting

| Member | What it decides | Source |
|---|---|---|
| `mode`, `sortOrder`, `maskInteraction` | Runtime equivalents of the Inspector fields | [TilemapRenderer API](https://docs.unity3d.com/ScriptReference/Tilemaps.TilemapRenderer.html) |
| `chunkSize` | Tiles per chunk — larger chunks batch more and cull more coarsely | [TilemapRenderer API](https://docs.unity3d.com/ScriptReference/Tilemaps.TilemapRenderer.html) |
| `detectChunkCullingBounds`, `chunkCullingBounds` | Runtime control of the culling estimate | [TilemapRenderer API](https://docs.unity3d.com/ScriptReference/Tilemaps.TilemapRenderer.html) |
| `maxChunkCount`, `maxFrameAge` | How many chunks stay cached and for how many unused frames — the memory-versus-rebuild dial for a large scrolling map | [TilemapRenderer API](https://docs.unity3d.com/ScriptReference/Tilemaps.TilemapRenderer.html) |
| `GetShaderUserValue()` / `SetShaderUserValue()` | Per-tile custom shader data, for effects that need per-cell input without a material per tile | [TilemapRenderer API](https://docs.unity3d.com/ScriptReference/Tilemaps.TilemapRenderer.html) |

`TilemapRenderer` derives from `Renderer`, so the standard material, bounds,
and shadow surface applies unchanged.
