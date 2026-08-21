# Rendering & Performance — Batching, Dynamic Atlas, UsageHints, Pooling

Sources: [UI Renderer](https://docs.unity3d.com/Manual/UIE-ui-renderer.html), [Control textures of the dynamic atlas](https://docs.unity3d.com/Manual/UIE-control-textures-of-the-dynamic-atlas.html), [`DynamicAtlasSettings` API](https://docs.unity3d.com/ScriptReference/UIElements.DynamicAtlasSettings.html), [Image import settings](https://docs.unity3d.com/Manual/UIE-image-import-settings.html), [Optimizing performance (Best Practice Guide)](https://docs.unity3d.com/Manual/best-practice-guides/ui-toolkit-for-advanced-unity-developers/optimizing-performance.html), [Performance consideration for runtime UI](https://docs.unity3d.com/Manual/UIE-performance-consideration-runtime.html), [`UsageHints` API](https://docs.unity3d.com/ScriptReference/UIElements.VisualElement-usageHints.html), [Work with vector graphics](https://docs.unity3d.com/Manual/ui-systems/work-with-vector-graphics.html), [Generate 2D visual content](https://docs.unity3d.com/Manual/UIE-generate-2d-visual-content.html), [Parallel tessellation](https://docs.unity3d.com/Manual/UIE-parallel-tessellation.html), [Best practices for managing elements](https://docs.unity3d.com/Manual/UIE-best-practices-for-managing-elements.html).
Covers: SKILL.md §4 — **"Keep draw-call batches intact: budget the dynamic atlas, animate transforms not layout, and pool elements with callbacks unregistered first"**.

The concrete thresholds and rules behind "why did this UI's draw calls
jump" — dynamic atlas exclusion, what breaks a shared batch, and the
element lifecycle choices that avoid GC pressure.

## Table of contents
- [Dynamic atlas](#dynamic-atlas)
- [What breaks batching](#what-breaks-batching)
- [VectorImage / SVG](#vectorimage--svg)
- [Custom mesh generation](#custom-mesh-generation)
- [Element lifecycle and pooling](#element-lifecycle-and-pooling)

## Dynamic atlas

| Subject | What it decides | Source |
|---|---|---|
| Default Size filter | **Textures larger than 64×64 are excluded from the dynamic atlas by default** — the concrete threshold that forces a separate draw call | [Control textures of the dynamic atlas](https://docs.unity3d.com/Manual/UIE-control-textures-of-the-dynamic-atlas.html) |
| `DynamicAtlasSettings` fields | `minAtlasSize`/`maxAtlasSize` (both powers of two, min ≤ max), `maxSubTextureSize` (exceeding it excludes a texture when the Size filter is active), `activeFilters`, `customFilter` delegate for per-texture opt-out | [`DynamicAtlasSettings` API](https://docs.unity3d.com/ScriptReference/UIElements.DynamicAtlasSettings.html) |
| Memory-constrained platforms | Lower Max Atlas Size to **2048px** as a starting point on mobile | [Control textures of the dynamic atlas](https://docs.unity3d.com/Manual/UIE-control-textures-of-the-dynamic-atlas.html) |
| What is eligible at all | Every image type not already atlased; Sprites imported as Sprite Mode = Multiple, or textures already placed in a static Sprite Atlas, are excluded from *dynamic* atlasing and use their own static atlas instead | [Image import settings](https://docs.unity3d.com/Manual/UIE-image-import-settings.html) |
| Import recommendations | Plain textures: Compression None, Alpha Is Transparency true, Non-Power-of-2 None. Sprites: Compression None, Alpha Is Transparency true, Mesh Type Tight | [Image import settings](https://docs.unity3d.com/Manual/UIE-image-import-settings.html) |
| Fragmentation | Heavy add/remove churn fragments the atlas over time; call `RuntimePanelUtils.ResetDynamicAtlas()` to reset it cleanly | [Control textures of the dynamic atlas](https://docs.unity3d.com/Manual/UIE-control-textures-of-the-dynamic-atlas.html) |

## What breaks batching

| Subject | What it decides | Source |
|---|---|---|
| Shared-batch requirement | Elements batch only when they share GPU state — same shader, same textures, same mesh data | [Optimizing performance](https://docs.unity3d.com/Manual/best-practice-guides/ui-toolkit-for-advanced-unity-developers/optimizing-performance.html) |
| Texture-per-batch limit | The UI Toolkit uber shader supports **up to 8 textures per batch**; exceeding it forces additional draw calls | [Optimizing performance](https://docs.unity3d.com/Manual/best-practice-guides/ui-toolkit-for-advanced-unity-developers/optimizing-performance.html) |
| Layout-property animation | Animating `width`/`height`/`left`/`top`/`position` forces a geometry rebuild every change — the most expensive thing to animate every frame | [Performance consideration for runtime UI](https://docs.unity3d.com/Manual/UIE-performance-consideration-runtime.html) |
| Mask nesting limit | Non-rectangular masks use the stencil buffer and support **up to 7 nested levels**; purely rectangular masks skip the stencil buffer and nest without limit | [Optimizing performance](https://docs.unity3d.com/Manual/best-practice-guides/ui-toolkit-for-advanced-unity-developers/optimizing-performance.html) |
| Custom materials | Any element on a non-default shader/material cannot share a batch with elements on the default UI shader | [Optimizing performance](https://docs.unity3d.com/Manual/best-practice-guides/ui-toolkit-for-advanced-unity-developers/optimizing-performance.html) |
| `UsageHints.DynamicTransform` / `.DynamicColor` / `.GroupTransform` | Keeps transform/color changes GPU-side instead of rebuilding geometry — the fix for animating a hierarchy every frame | [`UsageHints` API](https://docs.unity3d.com/ScriptReference/UIElements.VisualElement-usageHints.html) |
| Vertex Budget | Default `0` (automatic); raising it manually (e.g. to 20,000) can collapse several draw calls into one for complex UIs by avoiding buffer-resize-triggered splits | [Optimizing performance](https://docs.unity3d.com/Manual/best-practice-guides/ui-toolkit-for-advanced-unity-developers/optimizing-performance.html) |

**Critical caveat**: animate `translate`/`scale`/`rotate` (transform
properties) instead of `width`/`height`/`left`/`top` (layout properties)
wherever the visual effect allows it — this single substitution avoids the
per-frame relayout cost above and is why USS transitions in
[uss-styling-and-layout.md](uss-styling-and-layout.md) are recommended to
stay on transform properties.

## VectorImage / SVG

| Subject | What it decides | Source |
|---|---|---|
| Import as VectorImage | Set Generated Asset Type = "UI Toolkit Vector Image" on an imported SVG to get a `VectorImage` usable in USS `background-image`/UI Builder/runtime UI | [Work with vector graphics](https://docs.unity3d.com/Manual/ui-systems/work-with-vector-graphics.html) |
| SVG feature gap | Supports only a subset of SVG 1.1 — no text elements, per-pixel masking, filter effects, interactivity, or animation | [Work with vector graphics](https://docs.unity3d.com/Manual/ui-systems/work-with-vector-graphics.html) |
| `-no-graphics` gotcha | Starting the Editor with `-no-graphics` can break SVG import — avoid it while working with vector assets | [Work with vector graphics](https://docs.unity3d.com/Manual/ui-systems/work-with-vector-graphics.html) |
| Dynamic-atlas parity | Unconfirmed by the Manual whether `VectorImage` batches into the dynamic atlas the same way raster textures do — do not assume parity, per [root-links.md](root-links.md) | — |

## Custom mesh generation

| Subject | What it decides | Source |
|---|---|---|
| `MeshGenerationContext.Allocate()` | Low-level manual vertex/index allocation for custom `generateVisualContent` content | [Generate 2D visual content](https://docs.unity3d.com/Manual/UIE-generate-2d-visual-content.html) |
| `Painter2D` | Higher-level, Canvas-inspired vector drawing API (lines, arcs, shapes) for the same callback | [Generate 2D visual content](https://docs.unity3d.com/Manual/UIE-generate-2d-visual-content.html) |
| Parallel tessellation | Job-System-backed mesh generation for expensive custom content; `AddMeshGenerationJob()` for the simple case, `InsertMeshGenerationNode()`/`GetTempMeshAllocator()` for the expensive one — UI Toolkit waits for job completion automatically before reading the mesh | [Parallel tessellation](https://docs.unity3d.com/Manual/UIE-parallel-tessellation.html) |

## Element lifecycle and pooling

| Subject | What it decides | Source |
|---|---|---|
| Pool, don't `new()` | Reuse elements instead of instantiating repeatedly, per `performance-and-algorithms.md`'s pooling rule | [Best practices for managing elements](https://docs.unity3d.com/Manual/UIE-best-practices-for-managing-elements.html) |
| Unregister before pooling | An event callback left registered on a pooled-and-returned element keeps firing — unregister it first, per `coding-principles.md`'s Event handlers rule | [Best practices for managing elements](https://docs.unity3d.com/Manual/UIE-best-practices-for-managing-elements.html) |
| `ListView` built-in recycling | Already pools its row elements during scroll — prefer it over manually instantiating one element per data row | [Best practices for managing elements](https://docs.unity3d.com/Manual/UIE-best-practices-for-managing-elements.html) |
| Hide-vs-remove decision | `visibility: hidden` (drops render commands, keeps layout cost) → `opacity: 0` (still shaded on GPU) → `display: none` (recomputes sibling layout, zero GPU cost, data retained) → move off-screen (minimal CPU, still GPU-shaded) → `RemoveFromHierarchy()` (zero cost, all data freed) — pick by how soon the element reappears | [Best practices for managing elements](https://docs.unity3d.com/Manual/UIE-best-practices-for-managing-elements.html) |

**Critical caveat**: a cheap toggle that will reappear soon should use
`display`/`visibility`, not `RemoveFromHierarchy()` — removal is cheapest at
rest but costs a full rebuild to bring back, which can be worse than the
hidden element's idle cost if it toggles frequently.
