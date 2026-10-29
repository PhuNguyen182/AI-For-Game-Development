# Adapters

Pages: `/docs/adapters`, API `Adapter`, `FlexalonAspectRatioAdapter`, `FlexalonColliderAdapter`.

An adapter decides what a `SizeType.Component` axis measures and what happens to `localScale`/components after layout. "Wrong size" and "scale overwritten" are adapter questions.

## Default adapters (when `UseDefaultAdapter`, v4.3)
| Component | Measured | Scale |
|---|---|---|
| `TMP_Text` | Text size; `RectTransform` resized to fit | `FlexalonObject.Scale` |
| `RectTransform` | Rect size | `FlexalonObject.Scale` |
| `MeshRenderer` | Local bounds | Uniform where possible (mesh does not stretch to a non-uniform box) |
| `SpriteRenderer` | Sprite size | Uniform; depth scale 1 |
| `Collider` / `Collider2D` | Local bounds | Uniform where possible; 2D depth scale 1 |
| `Canvas` | Non-root and World Space adapted as `RectTransform`s | Root canvas size never modified (Unity owns it): put the layout on a child |
| `Image` | Only when exactly one axis is `Component`, from the sprite aspect | `FlexalonObject.Scale` |
| Empty GameObject | 1 per axis | none |

The mesh, sprite and collider adapters write `localScale`; a tween, clip or script writing it fights the pipeline. Route scale through `FlexalonObject.Scale`, or uncheck `UseDefaultAdapter` and size it yourself.

## Adapter components (one adapter wins per node, no stacking)
- `FlexalonAspectRatioAdapter`: keeps an explicit width:height ratio when one or two axes are set (placeholder frame, video surface).
- `FlexalonColliderAdapter`: resizes the collider to the Flexalon size instead of scaling the gameObject.
- `UseDefaultAdapter = false`: measures as empty, ignoring components (particle system, oversized mesh).

## `Adapter` interface
- `Measure(node, size, min, max)`: update only axes where `node.GetSizeType()` is `Component`, return bounds including the passed size and auto size, and clamp to `min`/`max` yourself; no later step corrects it.
- `TryGetScale(node, out scale)`: true plus desired local scale to modify scale.
- `TryGetRectSize(node, out rectSize)`: true plus desired rect size.
- Install: `Flexalon.GetOrCreateNode(go).SetAdapter(obj)`; read `FlexalonNode.Adapter` when diagnosing.
- Docs prose mentions `UpdateSize`; in the current API it is the `TryGetScale`/`TryGetRectSize` pair. Never touch the `Transform` inside an adapter.

## Wrong-size checks
| Symptom | Check |
|---|---|
| Size 1 for no reason | No measurable component, or `UseDefaultAdapter` unchecked |
| Image stretches | More than one axis `Component` |
| Canvas ignores its size | Root canvas |
| Number wrong, source unclear | `FlexalonResult.AdapterBounds` vs `LayoutBounds` |
