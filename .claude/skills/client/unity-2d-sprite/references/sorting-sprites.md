# Sorting Sprites — Draw Order, Sorting Group & Transparency Sort Mode

Sources: [2D rendering order](https://docs.unity3d.com/Manual/sprite/sort-sprites/sort-sprites.html), [Change the sorting order of 2D GameObjects](https://docs.unity3d.com/Manual/2d-renderer-sorting.html), [Sorting Group component reference](https://docs.unity3d.com/Manual/sprite/sorting-group/sorting-group-reference.html).
Covers: SKILL.md §4 — **"Set Sorting Layer and Order in Layer explicitly for every depth relationship the design states"**.

2D draw order is a chain of tie-breakers, not a single setting. Knowing where
in the chain a decision lands is what separates "set Order in Layer" from
"this needs a Sorting Group" from "this camera is sorting along the wrong
axis". A scene that configures none of it sorts on the last criterion by
default, which is why depth appears to change whenever something moves in Z.

## The chain, in evaluation order

| Step | What it decides | Source |
|---|---|---|
| 1. Sorting Layer | Wins outright over every criterion below it, regardless of position — layer order is set in Edit > Project Settings > Tags and Layers, where lower in the list draws in front | [2D rendering order](https://docs.unity3d.com/Manual/sprite/sort-sprites/sort-sprites.html) |
| 2. Order in Layer | Breaks ties inside one Sorting Layer; lower draws behind higher, and negative values are valid | [2D rendering order](https://docs.unity3d.com/Manual/sprite/sort-sprites/sort-sprites.html) |
| 3. Render Queue | The material's queue value, default 3000 for 2D — normally only relevant once a custom material is involved | [2D rendering order](https://docs.unity3d.com/Manual/sprite/sort-sprites/sort-sprites.html) |
| 4. Distance from camera | The fallback every unconfigured sprite lands on, computed from the camera's projection, its Transparency Sort Mode, and the renderer's Sprite Sort Point | [2D rendering order](https://docs.unity3d.com/Manual/sprite/sort-sprites/sort-sprites.html) |
| 5. Shader/material batching | Sprites sharing a material batch for draw-call efficiency, and relative order inside a batch is not guaranteed — never depend on it | [2D rendering order](https://docs.unity3d.com/Manual/sprite/sort-sprites/sort-sprites.html) |

## Transparency Sort Mode

| Mode | What it decides | Source |
|---|---|---|
| Default | Perspective for a perspective camera, orthographic for an orthographic one | [Change the sorting order of 2D GameObjects](https://docs.unity3d.com/Manual/2d-renderer-sorting.html) |
| Perspective / Orthographic | Forces one distance model regardless of the camera's projection | [Change the sorting order of 2D GameObjects](https://docs.unity3d.com/Manual/2d-renderer-sorting.html) |
| Custom Axis | Sorts along an explicit world axis — the correct setting for isometric and top-down games, where "further from camera" and "further up the screen" are different questions and the default answers the wrong one | [Change the sorting order of 2D GameObjects](https://docs.unity3d.com/Manual/2d-renderer-sorting.html) |

## Sorting Group

Groups a hierarchy so its renderers sort as one unit against the outside
world, keeping their own relative order internally. This is the answer to
multi-part characters interleaving with each other — a problem careful Order
in Layer numbering appears to solve until a second similar object overlaps the
same range.

| Property | What it decides | Source |
|---|---|---|
| Sorting Layer / Order in Layer | The whole group's position in the chain above; children keep their relative order inside it | [Sorting Group component reference](https://docs.unity3d.com/Manual/sprite/sorting-group/sorting-group-reference.html) |
| Sorting Type — Default | Sorts alongside sibling Sorting Groups at the same hierarchy level | [Sorting Group component reference](https://docs.unity3d.com/Manual/sprite/sorting-group/sorting-group-reference.html) |
| Sorting Type — Sort at Root | Sorts at the top of the hierarchy, ignoring any parent Sorting Group — use when a nested group must escape its parent's band | [Sorting Group component reference](https://docs.unity3d.com/Manual/sprite/sorting-group/sorting-group-reference.html) |
| Sorting Type — Sort 3D as 2D | Sorts at root and ignores 3D Z values inside the group, so mixed 2D/3D content orders purely as 2D | [Sorting Group component reference](https://docs.unity3d.com/Manual/sprite/sorting-group/sorting-group-reference.html) |
