# Sorting Sprites

Pages: https://docs.unity3d.com/Manual/sprite/sort-sprites/sort-sprites-landing.html, https://docs.unity3d.com/Manual/sprite/sorting-group/sorting-group-reference.html

## Chain, evaluated in order

1. **Sorting Layer** wins outright. Order set in Edit > Project Settings > Tags and Layers; lower in the list draws in front.
2. **Order in Layer** breaks ties inside a layer; lower draws behind higher; negatives valid.
3. **Render Queue** of the material (default 3000 for 2D); matters with custom materials.
4. **Distance from camera**, the fallback for unconfigured sprites, from the camera projection, Transparency Sort Mode and the renderer's Sprite Sort Point (Center or Pivot).
5. **Shader/material batching**: order inside a batch is not guaranteed; never depend on it.

An unconfigured scene sorts on step 4, so depth appears to change whenever something moves in Z.

## Transparency Sort Mode

| Mode | Decision |
|---|---|
| Default | Perspective for a perspective camera, orthographic for orthographic |
| Perspective / Orthographic | Forces one distance model |
| Custom Axis | Sorts along an explicit world axis; correct for isometric/top-down, where "further from camera" and "further up the screen" differ. Isometric value (0, 1, 0) is in `unity-tilemap` |

## Sorting Group

Sorts a hierarchy as one unit against the outside world, keeping internal relative order. Fixes multi-part characters interleaving, which Order in Layer numbering only appears to solve until a second similar object overlaps the same range.

| Sorting Type | Decision |
|---|---|
| Default | Sorts with sibling groups at the same hierarchy level |
| Sort at Root | Sorts at the top, ignoring any parent Sorting Group; for a nested group that must escape its parent's band |
| Sort 3D as 2D | Sort at Root plus ignoring 3D Z inside the group, for mixed 2D/3D content |

Sorting Layer / Order in Layer on the group place the whole group in the chain.
