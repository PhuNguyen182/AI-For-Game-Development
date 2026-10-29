# RectTransform, Anchors, Auto Layout

`RectTransform` adds width/height to a Transform. The Rect Tool changes width/height, not scale, so resizing does not distort fonts, sliced borders or child layout.

- **Pivot**: 0–1 point that rotation, scaling and sizing happen around; a corner pivot rotates around the corner.
- **Anchors** tie a child to fractions of the parent (0 = left/bottom, 1 = right/top).
  - Together (fixed point): Inspector shows `Pos X/Y`, `Width`, `Height`; constant pixel size and offset.
  - Split (stretch): shows `Left/Right/Top/Bottom` padding; size tracks the parent. This is what makes a panel responsive.
- Anchor Presets set common configs per axis. The "R" raw-edit toggle changes anchor/pivot without position compensation, so the element visually jumps unless the offset is adjusted.
- Pair anchors with `CanvasScaler` ([canvas-and-scaling.md](canvas-and-scaling.md)).

## Auto Layout
- **Layout Element**: overrides the min/preferred/flexible size one child reports to its layout controller. Use it for one exception under a shared group instead of a special group.
- **Content Size Fitter**: sizes itself to content; Horizontal/Vertical Fit = Preferred makes a label or tooltip hug its text.
- **Horizontal / Vertical / Grid Layout Group**: control every child's size and position (padding, spacing, alignment, control-child-size, use-child-scale, child-force-expand). A group also implements `ILayoutElement`, so nested groups work, but an inner change can rebuild every ancestor group in the same frame.
- **Aspect Ratio Fitter**: fixed aspect (fit-in-parent, envelope-parent, one axis drives the other) for content that must not distort.
- **One layout owner per size**: never give a `RectTransform` a fixed size or a tween on a property a Layout Group / Content Size Fitter / Flexalon also controls; the last to run wins silently. A tween that must move a laid-out size should drive `LayoutElement` min/preferred/flexible instead.

## Calculation order
Four passes: horizontal size bottom-up, horizontal set top-down, then the same for vertical. Heights may depend on resolved widths, never the reverse; width-from-height (e.g. aspect-locked width from wrapped text height) needs a custom component or a two-frame settle.

## Custom layout
`ILayoutElement` (reports sizes), `ILayoutGroup`/`ILayoutController` (positions children), `ILayoutSelfController` (resizes itself), `ILayoutIgnorer` (child opts out of its group). Try Layout Element overrides or existing group settings first; see [scripting-api-and-extensibility.md](scripting-api-and-extensibility.md).
