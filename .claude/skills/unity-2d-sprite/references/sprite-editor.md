# Sprite Editor

Edits the texture's import settings, shared by every sprite it cuts. Open: select the texture (Texture Type Sprite), **Open Sprite Editor** (needs the 2D Sprite package). Pages: https://docs.unity3d.com/Manual/sprite/sprite-editor/sprite-editor-window-reference-landing.html

Nothing reaches the asset until **Apply**; closing the window or switching modules discards pending edits without warning. Preview shows pending edits in the Scene view before Apply. The Skinning Editor belongs to the 2D Animation package, out of scope. Color toggles an alpha-only view, useful for judging outlines.

## Slicing

| Control | Decision |
|---|---|
| Slice type | **Automatic** splits by transparent boundaries and merges touching sprites; **Grid By Cell Size** / **Grid By Cell Count** are the only safe choices on a tightly packed sheet; **Isometric Grid** cuts diamonds (Is Alternate staggers) |
| Method | **Delete Existing** rebuilds every rect and breaks clips/prefabs resolving sprites by name; **Smart** preserves still-matching names, borders, pivots; **Safe** only adds rects |
| Keep Empty Rects | Keeps blank cells; needed when animation timing depends on blank frames |
| Offset / Padding | Pixel offset from the edge and spacing between rects; fixes a grid landing one pixel off |
| Pivot / Pivot Unit Mode | Default pivot for generated rects (Normalized or Pixels) |
| Locks (Multiple) | Lock Name/Size/Position/Border/Create-Delete so a re-slice cannot disturb tuned values |
| Trim | Shrinks the selected rect to opaque pixels |

Per-sprite fields: **Name** is the sub-sprite asset name and the key clips resolve frames by, so renaming breaks bindings silently; Position X/Y/W/H in pixels; Border L/R/T/B (9-slice); Pivot / Custom Pivot.

## Custom Outline (render mesh)

Trims the mesh the GPU rasterises. Effective only at Mesh Type Tight; an outline authored at Full Rect saves and renders nothing. Not interchangeable with the physics shape.

| Control | Decision |
|---|---|
| Outline Detail | Tighter trace shades fewer pixels but submits more vertices; reverses on a mostly opaque sprite |
| Alpha Tolerance | Alpha below which a pixel is transparent; raise when anti-aliased edges pull the outline outward |
| Snap | Snaps vertices to the pixel grid (avoids half-pixels in pixel art) |
| Generate / Generate All | Selected sprite / only sprites with no outline yet (safe bulk) |
| Force Generate All | Overwrites every outline including hand edits, behind a confirmation checkbox; destructive |
| Copy / Paste / Paste All; Paste from Custom Physics Shape | Transfer outlines; the paste-from reuses the collision outline as render mesh |

## Custom Physics Shape (collision outline on the `Sprite`)

Read back via `Sprite.GetPhysicsShape`. A `Collider2D` with **Use Sprite Physics Shape**, or a sprite imported with Generate Physics Shape and no custom shape, adopts it, so one pass serves every instance. Same controls as Custom Outline, except:

- Outline Detail is a runtime cost dial (vertices are paid per collision check), not a fidelity dial.
- Alpha Tolerance decides whether soft edges are inside the hitbox.
- **Paste from Custom Outline** reuses the render outline as collision.
- **Edit Collider** diverges one instance from the shared shape; easy to forget, use only when that instance truly differs.

Edit gestures (both modules): drag a vertex to move, click an edge to insert, select + Delete to remove, Ctrl+drag an edge to move it.

## Secondary Textures

Up to 8 extra textures per sprite (Add +, assign texture, set Name, Apply), looked up by shader property name.

- Name `_NormalMap` for a normal map, `_MaskTex` for a lighting mask; the URP 2D lit shaders look up exactly these. Any other name binds nothing, errors nothing, lights nothing; a custom name works only for a shader declaring that property.
- Every sprite packed into one atlas must carry the same number of secondary textures; a mismatch fails at pack time. Check Pack Preview's secondary-texture dropdown (sprite-atlas.md).
- `Light2D` rig: `unity-urp-rendering`.
