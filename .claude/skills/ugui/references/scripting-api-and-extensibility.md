# Extending uGUI

Unverified against 2.6: the API shape is the long-stable `com.unity.ugui@1.0` surface; check a member's signature in the installed Editor. `Canvas` and `CanvasGroup` live in `UnityEngine`, not `UnityEngine.UI`; TMP types are in `TMPro` (`TMP_Text` base, `TextMeshProUGUI`, `TMP_TextInfo` for per-character/link hit-testing).

- **Custom visual**: subclass `Graphic` (or `MaskableGraphic` to support `Mask`/`RectMask2D`) and override `OnPopulateMesh(VertexHelper vh)`. Never push geometry to a `Mesh` outside it; `CanvasRenderer` needs it there for batching and rebuilds.
- **Effect on an existing Graphic**: implement `IMeshModifier` (`BaseMeshEffect`, base of `Shadow`/`Outline`).
- **Custom layout**: `ILayoutElement` for sizes; subclass `LayoutGroup` for an arrangement algorithm; `ILayoutIgnorer` to hand-place one child. See [rect-transform-and-layout.md](rect-transform-and-layout.md).
- **Custom input**: implement the `IPointer*`/`IDrag*`/`ISelectHandler` interfaces rather than polling in `Update`; custom modules per [event-system-and-input.md](event-system-and-input.md).
- **Rebuild timing**: implement `ICanvasElement` and register with `CanvasUpdateRegistry`, or hook `Canvas.willRenderCanvases`, to defer recalculation instead of recomputing on every property set. Use when a custom component shows extra rebuilds in the UI Profiler.
- Write a custom component only when `LayoutElement` overrides, group settings or a composition of built-ins cannot express it (e.g. a fill shape no Fill Method supports).
