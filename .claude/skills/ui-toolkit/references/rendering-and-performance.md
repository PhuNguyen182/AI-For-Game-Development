# Rendering and performance

Sources: [Dynamic atlas](https://docs.unity3d.com/Manual/UIE-control-textures-of-the-dynamic-atlas.html), [DynamicAtlasSettings](https://docs.unity3d.com/ScriptReference/UIElements.DynamicAtlasSettings.html), [Image import](https://docs.unity3d.com/Manual/UIE-image-import-settings.html), [BPG perf](https://docs.unity3d.com/Manual/best-practice-guides/ui-toolkit-for-advanced-unity-developers/optimizing-performance.html), [Runtime perf](https://docs.unity3d.com/Manual/UIE-performance-consideration-runtime.html), [UsageHints](https://docs.unity3d.com/ScriptReference/UIElements.VisualElement-usageHints.html), [Vector](https://docs.unity3d.com/Manual/ui-systems/work-with-vector-graphics.html), [2D content](https://docs.unity3d.com/Manual/UIE-generate-2d-visual-content.html), [Tessellation](https://docs.unity3d.com/Manual/UIE-parallel-tessellation.html), [Elements](https://docs.unity3d.com/Manual/UIE-best-practices-for-managing-elements.html).

## Dynamic atlas
- Textures larger than 64×64 are excluded by default (the Size filter): each costs a separate draw call.
- `DynamicAtlasSettings`: `minAtlasSize`/`maxAtlasSize` (powers of two, min ≤ max), `maxSubTextureSize`, `activeFilters`, `customFilter` (per-texture opt-out).
- On memory-constrained mobile start with Max Atlas Size 2048.
- Sprites with Sprite Mode = Multiple, or already in a static Sprite Atlas, use their own atlas, not the dynamic one.
- Import: textures Compression None, Alpha Is Transparency on, Non-Power-of-2 None; sprites Compression None, Alpha Is Transparency on, Mesh Type Tight.
- Heavy add/remove fragments the atlas: `RuntimePanelUtils.ResetDynamicAtlas()`.

## What breaks batching
- Batching needs shared GPU state (shader, textures, mesh data). The uber shader takes up to 8 textures per batch.
- A custom shader/material on an element cannot share a batch with default-shader elements.
- Non-rectangular masks use the stencil buffer, nest up to 7 levels; rectangular masks nest without limit.
- Animating `width`/`height`/`left`/`top`/`position` rebuilds geometry on every change: animate `translate`/`scale`/`rotate` instead (and keep USS transitions on them).
- `UsageHints.DynamicTransform` / `.DynamicColor` / `.GroupTransform` keep transform/color changes GPU-side: the fix for animating a hierarchy every frame.
- Vertex Budget default `0` (automatic); raising it (e.g. 20,000) can merge draw calls in complex UIs by avoiding buffer-resize splits.

## VectorImage / SVG
- Set Generated Asset Type = "UI Toolkit Vector Image" on the SVG for use in USS `background-image`/UI Builder.
- SVG import and `VectorImage` in USS `background-image`/UI Builder need the optional `com.unity.vectorgraphics` package (Sprite needs `com.unity.2d.sprite`).
- Only a subset of SVG 1.1: no text, per-pixel masking, filters, interactivity, animation.
- `-no-graphics` can break SVG import.
- Unverified: whether `VectorImage` batches in the dynamic atlas like raster textures. Do not assume parity.

## Custom mesh
- `generateVisualContent`: `MeshGenerationContext.Allocate()` (manual vertices/indices) or `Painter2D` (lines, arcs, shapes).
- Parallel tessellation: `AddMeshGenerationJob()` (simple) or `InsertMeshGenerationNode()`/`GetTempMeshAllocator()` (expensive); UI Toolkit waits for job completion.

## Elements and pooling
- Pool instead of `new()` (`csharp-standards` → `performance-and-algorithms.md`). Unregister callbacks before returning an element to a pool, or it keeps firing.
- `ListView` already recycles rows: prefer it over one element per data row.
- Hide vs remove, by how soon it reappears: `visibility: hidden` (no render commands, keeps layout cost) → `opacity: 0` (still shaded) → `display: none` (sibling relayout, no GPU cost, data kept) → off-screen (low CPU, still shaded) → `RemoveFromHierarchy()` (zero cost, data freed, full rebuild to return). A frequently toggled element should use `display`/`visibility`.
