# Scripting API and Extensibility

Source: [Unity UI and TextMesh Pro Scripting API](https://docs.unity3d.com/Packages/com.unity.ugui@2.6/api/index.html), general `UnityEngine.UI`/`UnityEngine.EventSystems` API shape (stable since `com.unity.ugui@1.0` — see the Disclosed gaps note in [root-links.md](root-links.md) for how this file was sourced).
Covers: SKILL.md §4 — "Extend by subclassing `Graphic`/`LayoutGroup`, never by hacking a built-in component's serialized fields", "Build custom UI geometry through `VertexHelper`, never raw mesh arrays".

## Namespaces

| Namespace | Holds |
|---|---|
| `UnityEngine.UI` | Every visual/interaction/layout component — `Graphic`, `MaskableGraphic`, `Image`, `RawImage`, `Text`, `Selectable`, `Button`, `Toggle`, `Slider`, `Scrollbar`, `Dropdown`, `InputField`, `ScrollRect`, `Mask`, `RectMask2D`, `LayoutGroup` and its Horizontal/Vertical/Grid subclasses, `LayoutElement`, `ContentSizeFitter`, `AspectRatioFitter`, `CanvasScaler` |
| `UnityEngine.EventSystems` | `EventSystem`, `BaseInputModule`/`PointerInputModule`/`StandaloneInputModule`, `GraphicRaycaster`, `PhysicsRaycaster`, `Physics2DRaycaster`, `EventTrigger`, `ExecuteEvents`, and the `IPointer*Handler`/`IDrag*Handler`/`ISelectHandler`/etc. interfaces from [event-system-and-input.md](event-system-and-input.md) |
| `TMPro` | `TMP_Text` (the base both UI and 3D TMP objects share), `TextMeshProUGUI` (the UI/Canvas variant), `TMP_InputField`, `TMP_Dropdown`, `TMP_FontAsset`, `TMP_SpriteAsset`, `TMP_StyleSheet`, `TMP_TextInfo` (per-character/word/line/link geometry and hit-testing) |

`Canvas` and `CanvasGroup` themselves live in `UnityEngine`, not
`UnityEngine.UI` — they predate the package split.

## Extending a Graphic

Subclass `Graphic` (or `MaskableGraphic` to also support `Mask`/`RectMask2D`
clipping) and override `OnPopulateMesh(VertexHelper vh)` to emit custom
geometry — this is the mechanism behind every built-in visual component,
and the right one for a genuinely custom-rendered UI element that isn't
just a styled `Image`. Never mutate `Graphic`'s vertex output by
manipulating a `Mesh` directly outside `OnPopulateMesh`; `CanvasRenderer`
expects geometry through that call so it can participate in batching and
Canvas rebuilds correctly.

An `IMeshModifier` implementation (e.g. `BaseMeshEffect`, which `Shadow`
and `Outline` both derive from) intercepts and modifies the mesh a
`Graphic` already produced, without owning generation itself — the right
choice for an effect layered onto an existing Graphic rather than a whole
new visual component.

## Extending layout

Per [rect-transform-and-layout.md](rect-transform-and-layout.md),
implement `ILayoutElement` to report custom min/preferred/flexible sizes,
or subclass `LayoutGroup` (which already implements `ILayoutElement` +
`ILayoutGroup` + `ILayoutController`) for a custom arrangement algorithm.
`ILayoutIgnorer` opts a child out of its parent Layout Group's control
entirely, for the rare case where one child must be positioned by hand
inside an otherwise auto-laid-out parent.

## Extending input

A custom `Selectable`-adjacent interaction implements the relevant
`IPointer*`/`IDrag*`/`ISelectHandler` interfaces directly (per
[event-system-and-input.md](event-system-and-input.md)) rather than
polling pointer state in `Update`. A custom Input Module subclasses
`BaseInputModule`/`PointerInputModule` — escalation territory, per that
same file.

## `ICanvasElement` and rebuild timing

Components that need to react to a Canvas geometry rebuild (rather than
just render once) implement `ICanvasElement` and register with
`CanvasUpdateRegistry`, or hook `Canvas.willRenderCanvases`. This is the
mechanism a custom layout or custom Graphic uses to defer its own
recalculation until the right point in the rebuild pipeline, instead of
recomputing eagerly on every property set — relevant when a custom
component's naive implementation shows up as extra Canvas rebuilds in the
UI Profiler (see [profiling-performance-and-howtos.md](profiling-performance-and-howtos.md)).

## When to reach for a custom component at all

Per YAGNI in `coding-principles.md`: a `LayoutElement` override, an
existing Layout Group's settings, or composing several built-in components
covers most "custom UI" requests without a new `Graphic`/`LayoutGroup`
subclass. Write one only once a built-in composition genuinely can't
express the requirement — e.g. a fill shape no `Image` Fill Method
supports, or a layout algorithm no combination of Horizontal/Vertical/Grid
Layout Group can produce.
