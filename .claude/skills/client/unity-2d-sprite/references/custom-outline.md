# Custom Outline — Sprite Render Mesh

Sources: https://docs.unity3d.com/Manual/sprite/sprite-editor/generate-outline.html, https://docs.unity3d.com/Manual/sprite/sprite-editor/custom-outline-editor-reference.html

## Purpose

The Custom Outline module defines the mesh Unity actually renders for a sprite — i.e. it removes transparent pixels from the render mesh so Unity doesn't waste fragment shader work drawing fully-transparent quad area. It only applies when **Mesh Type = Tight** in the sprite's import settings (see [import-settings.md](import-settings.md)); Full Rect sprites render as a plain quad regardless of any outline authored here.

This is a rendering-mesh concern, distinct from the **Custom Physics Shape** module (collision geometry) — see [custom-physics-shape.md](custom-physics-shape.md). The two are visually similar workflows but feed entirely different systems; don't conflate them.

## Toolbar controls

| Control | Behavior |
|---|---|
| Outline Detail | Higher values trace the opaque region more closely (more vertices, closer fit); lower values simplify the shape (fewer vertices, cheaper mesh) — trades render-mesh fidelity against vertex count/GPU cost. |
| Alpha Tolerance | The alpha threshold below which a pixel counts as transparent for outline tracing purposes. |
| Snap | Snaps outline vertices to the nearest pixel. |
| Generate | Traces a fresh outline for the currently selected sprite from its opaque pixels. |
| Generate All | Generates outlines only for sprites in the sheet that don't already have one. |
| Force Generate All | Regenerates outlines for every sprite, overwriting any existing hand-edited outline (requires an explicit confirmation checkbox — it's destructive to manual edits). |
| Copy / Paste / Paste All | Transfers an outline shape between sprites. |
| Paste from Custom Physics Shape | Copies the physics-shape outline over as the render outline (or vice versa from that module) when both should share the same geometry. |

## Editing

- **Move a vertex**: click and drag it.
- **Add a vertex**: click on an edge.
- **Delete a vertex**: select it and press Delete.
- **Move an edge**: Ctrl+drag it.

## Practical guidance

- Only invest in a tight custom outline when the sprite has significant transparent padding relative to its opaque silhouette (e.g. a small circular icon in a large square texture) — for a sprite that's already mostly opaque, Full Rect mesh is simpler and the outline pass adds nothing (KISS in `coding-principles.md`).
- Don't crank **Outline Detail** to maximum by default — per `performance-and-algorithms.md`'s hardware-friendly-execution principle, an overly detailed render mesh adds vertex count for a visual difference that's usually imperceptible; tune it to the lowest detail that still reads as the sprite's silhouette.
- **Force Generate All** discards any hand-tuned outline edits across the whole sheet — treat it as a destructive action to confirm deliberately, not a routine button to click.
