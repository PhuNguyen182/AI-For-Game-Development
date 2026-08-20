# Tilemap Renderer Component

Sources: https://docs.unity3d.com/Manual/tilemaps/work-with-tilemaps/tilemap-renderer-reference.html, `UnityEngine.Tilemaps.TilemapRenderer` scripting API

## Inspector properties

| Property | Description |
|---|---|
| Sort Order | Direction tiles sort within a chunk: **Bottom Left** (default), **Bottom Right**, **Top Left**, **Top Right**. |
| Mode | **Chunk** (batched, best performance), **Individual** (each tile renders separately — needed to depth-sort tiles against non-tilemap sprites), **SRP Batch** (uses the Scriptable Render Pipeline Batcher). |
| Detect Chunk Culling Bounds | **Auto** (estimated from sprite bounds) or **Manual**. |
| Chunk Culling Bounds | Extra culling-boundary distance, in units (Manual only). |
| Mask Interaction | **None**, **Visible Inside Mask**, **Visible Outside Mask** — same semantics as `SpriteRenderer`'s Mask Interaction, see `unity-2d-sprite`'s [sprite-mask.md](../../unity-2d-sprite/references/sprite-mask.md). |
| Material | Default `Sprite-Lit-Default`; swap only for a specific shader requirement — shader authoring itself is `technical-artist`'s/`shader-authoring`'s territory. |
| Sorting Layer / Order in Layer | Same semantics as `SpriteRenderer` — see `unity-2d-sprite`'s [sorting-sprites.md](../../unity-2d-sprite/references/sorting-sprites.md). |
| Rendering Layer Mask | Assigns rendering layers, e.g. for `Light2D` layer filtering (`unity-urp-rendering`'s territory). |

## Scripting API surface

| Member | Description |
|---|---|
| `mode` | Script-side equivalent of the Mode setting. |
| `sortOrder` | Script-side equivalent of Sort Order. |
| `chunkSize` | Tile count per chunk. |
| `detectChunkCullingBounds`, `chunkCullingBounds` | Script-side equivalents of the culling settings. |
| `maskInteraction` | Script-side equivalent of Mask Interaction. |
| `maxChunkCount` | Maximum chunks cached in memory. |
| `maxFrameAge` | Maximum frames an unused chunk stays cached before eviction. |
| `GetShaderUserValue()` / `SetShaderUserValue()` | Per-tile custom shader data. |

Inherits the standard `Renderer` API (materials, bounds, `enabled`, shadow settings) since `TilemapRenderer` is a `Renderer` subclass.

## Practical guidance

- Use **Individual** mode only when tiles genuinely need to depth-sort against other sprites (e.g. a top-down game where the player walks behind a tall tile) — **Chunk** mode is the default and meaningfully cheaper for anything that doesn't need per-tile sort interleaving, per `performance-and-algorithms.md`'s draw-call/batching discipline.
- Set **Detect Chunk Culling Bounds = Manual** with an explicit value when tiles include GameObject-brush content or oversized sprites that extend past the auto-estimated bounds — an under-estimated culling bound causes visible pop-in at chunk edges.
