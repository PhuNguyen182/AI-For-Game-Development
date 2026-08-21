# Custom Outline — Sprite Render Mesh

Sources: [Crop a sprite](https://docs.unity3d.com/Manual/sprite/sprite-editor/generate-outline.html), [Custom Outline tab reference](https://docs.unity3d.com/Manual/sprite/sprite-editor/custom-outline-editor-reference.html).
Covers: SKILL.md §4 — **"Pick Mesh Type by whether the sprite is 9-sliced, not by overdraw instinct"**, escalation branch.

Custom Outline trims the mesh Unity actually rasterises, so the GPU stops
shading fully transparent quad area. It has effect **only** at Mesh Type
Tight — a Full Rect sprite draws as a plain quad no matter what outline is
authored here. It is a rendering concern and is not interchangeable with
[custom-physics-shape.md](custom-physics-shape.md), which looks like the same
workflow and feeds an entirely different system.

## Controls

| Control | What it decides | Source |
|---|---|---|
| Outline Detail | Trades fit against vertex count — a tighter trace shades fewer pixels but submits more vertices, so the win reverses on a sprite that is already mostly opaque | [Custom Outline tab reference](https://docs.unity3d.com/Manual/sprite/sprite-editor/custom-outline-editor-reference.html) |
| Alpha Tolerance | The alpha below which a pixel counts as transparent when tracing — raise it when anti-aliased edges pull the outline outward | [Custom Outline tab reference](https://docs.unity3d.com/Manual/sprite/sprite-editor/custom-outline-editor-reference.html) |
| Snap | Snaps vertices to the pixel grid, which is what keeps a pixel-art outline from sitting on half-pixels | [Custom Outline tab reference](https://docs.unity3d.com/Manual/sprite/sprite-editor/custom-outline-editor-reference.html) |
| Generate | Traces the selected sprite only | [Custom Outline tab reference](https://docs.unity3d.com/Manual/sprite/sprite-editor/custom-outline-editor-reference.html) |
| Generate All | Traces only sprites that have no outline yet — the safe bulk action | [Custom Outline tab reference](https://docs.unity3d.com/Manual/sprite/sprite-editor/custom-outline-editor-reference.html) |
| Force Generate All | Overwrites every outline on the sheet including hand edits, behind a confirmation checkbox — destructive, and not a re-sync button | [Custom Outline tab reference](https://docs.unity3d.com/Manual/sprite/sprite-editor/custom-outline-editor-reference.html) |
| Copy / Paste / Paste All | Transfers an outline between sprites | [Custom Outline tab reference](https://docs.unity3d.com/Manual/sprite/sprite-editor/custom-outline-editor-reference.html) |
| Paste from Custom Physics Shape | Reuses the collision outline as the render mesh when both should match — the only sanctioned way to keep the two in sync | [Custom Outline tab reference](https://docs.unity3d.com/Manual/sprite/sprite-editor/custom-outline-editor-reference.html) |

## Editing gestures

| Gesture | Effect | Source |
|---|---|---|
| Drag a vertex | Moves it | [Crop a sprite](https://docs.unity3d.com/Manual/sprite/sprite-editor/generate-outline.html) |
| Click an edge | Inserts a vertex | [Crop a sprite](https://docs.unity3d.com/Manual/sprite/sprite-editor/generate-outline.html) |
| Select a vertex, press Delete | Removes it | [Crop a sprite](https://docs.unity3d.com/Manual/sprite/sprite-editor/generate-outline.html) |
| Ctrl+drag an edge | Moves the whole edge | [Crop a sprite](https://docs.unity3d.com/Manual/sprite/sprite-editor/generate-outline.html) |

**Critical caveat**: an outline authored while Mesh Type is Full Rect saves
without complaint and renders nothing — check the import setting first when a
carefully traced outline appears to have no effect.
