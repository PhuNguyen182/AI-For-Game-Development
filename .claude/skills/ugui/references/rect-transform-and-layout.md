# RectTransform, Anchors, and Auto Layout

Source: [Basic Layout](https://docs.unity3d.com/Packages/com.unity.ugui@2.6/manual/UIBasicLayout.html), [Auto Layout](https://docs.unity3d.com/Packages/com.unity.ugui@2.6/manual/UIAutoLayout.html).
Covers: SKILL.md §4 — "Anchor before you position", "Let a Layout Group and Content Size Fitter own child sizing, never both a fixed size and a layout controller on the same RectTransform".

## RectTransform — Transform plus a rectangle

`RectTransform` replaces `Transform` on every UI GameObject: it carries
position/rotation/scale like a normal Transform, plus a width and height.
The Rect Tool resizing a RectTransform changes width/height directly rather
than local scale — unlike a 2D sprite or 3D mesh — so resizing a panel does
not distort font size, sliced-image borders, or child layout the way
scaling would.

### Pivot

The pivot is the point rotation, scaling, and sizing operations happen
around. Its position (as a 0–1 fraction of the rectangle) changes the visual
outcome of every one of those operations — a pivot at a corner rotates
around that corner, not the visual center.

### Anchors

Anchors tie a child rectangle to a fraction of its parent rectangle, shown
as four triangular handles in the Scene view. Anchor values are fractions
of the parent's width/height: `0.0` = left/bottom, `0.5` = middle, `1.0` =
right/top.

- **Anchors together** (a fixed anchor point): the Inspector shows `Pos X`,
  `Pos Y`, `Width`, `Height` — the element keeps a constant pixel size and
  constant offset from that anchor point regardless of parent resizing.
- **Anchors split apart** (a stretch anchor): the Inspector instead shows
  `Left`, `Right`, `Top`, `Bottom` — padding values from each edge to its
  corresponding anchor. The element's size now tracks the parent's size,
  which is what makes a panel genuinely responsive rather than pixel-fixed.

The **Anchor Presets** button in the Inspector is the fast path to a common
configuration (stretch-both, corner-anchored, center-anchored, etc.),
settable independently per axis. The "R" (raw edit) toggle lets anchor/pivot
values change without Unity's automatic position compensation — useful when
restructuring a hierarchy, but it will visually reposition the element
unless the offset is also adjusted.

**Anchoring is the mechanism that makes a screen resolution-independent
before `CanvasScaler` ever enters the picture** — per
[canvas-and-scaling.md](canvas-and-scaling.md)'s Match-slider guidance,
combine both: anchors solve *where on the screen* an element sits at any
aspect ratio, `CanvasScaler` solves *how big* everything is at any
resolution. Neither alone is sufficient for a genuinely responsive PC +
mobile HUD, per `coding-principles.md`'s responsive-UI expectation.

## Auto Layout

Three kinds of component cooperate to size and position children without
hand-placing each `RectTransform`:

### Layout Element

Overrides the minimum/preferred/flexible size a specific GameObject reports
to whatever layout controller is above it, by checking a box and entering
a value per property. Use it to make one particular child behave
differently from its siblings under a shared Layout Group, rather than
building a special-cased layout group for that one exception.

### Content Size Fitter

Makes a GameObject size *itself* to fit its own content. Setting Horizontal
Fit and/or Vertical Fit to **Preferred** makes the RectTransform grow/shrink
to fit e.g. a Text component's content — the standard pattern behind a
label or tooltip that must hug its text rather than carry a fixed size.

### Layout Groups

`Horizontal Layout Group`, `Vertical Layout Group`, and `Grid Layout Group`
control the size and position of every child under them (padding, spacing,
child alignment, control-child-size, use-child-scale, child-force-expand).
A Layout Group is itself both a layout controller for its children and,
because it also implements `ILayoutElement`, something a parent Layout
Group can measure and size in turn — which is what makes nested layout
groups work, and also what makes them expensive: a change to an inner
group can force a rebuild that ripples up through every ancestor layout
group on the same frame.

### Aspect Ratio Fitter

Keeps a fixed aspect ratio on a RectTransform — fit-in-parent, envelope-
parent, or drive one axis from the other — for content like a video feed
or a portrait/thumbnail that must never distort.

### Layout calculation order

Layout resolves in four passes: horizontal size calculation bottom-up, then
horizontal size setting top-down, then the same two passes for vertical.
**Calculated heights may depend on already-resolved widths, but widths can
never depend on heights** — a layout that tries to make width depend on
height (e.g. an aspect-locked width from a wrapped text block's resulting
height) cannot be expressed through the built-in system in one pass and
needs a custom component or a two-frame settle.

### Custom layout components

Three interfaces back every built-in layout behavior and are the extension
point for a custom one: `ILayoutElement` (reports min/preferred/flexible
size), `ILayoutGroup`/`ILayoutController` (positions children), and
`ILayoutSelfController` for a component that resizes only itself (like
Content Size Fitter). See
[scripting-api-and-extensibility.md](scripting-api-and-extensibility.md)
before writing one from scratch — a `LayoutElement` override or a
combination of existing Layout Group settings covers most cases without a
new class, per KISS in `coding-principles.md`.
