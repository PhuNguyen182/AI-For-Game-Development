# Sorting Sprites — 2D Rendering Order

Sources: https://docs.unity3d.com/Manual/sprite/sort-sprites/sort-sprites-landing.html, https://docs.unity3d.com/Manual/sprite/sort-sprites/sort-sprites.html, https://docs.unity3d.com/Manual/2d-renderer-sorting.html, https://docs.unity3d.com/Manual/sprite/sorting-group/sorting-group-reference.html

## The sort order — in priority

Unity decides which of two overlapping 2D GameObjects draws in front using these criteria, evaluated in order (later criteria only break ties left by earlier ones):

1. **Sorting Layer** — a GameObject on a Sorting Layer higher in the project's Sorting Layers list (Edit > Project Settings > Tags and Layers) renders in front of one on a lower layer, regardless of any other setting.
2. **Order in Layer** — within the same Sorting Layer, a lower value renders behind a higher value (e.g. Order in Layer −1 is behind Order in Layer 3).
3. **Render Queue** — a lower material Render Queue value renders earlier (default 2D value: 3000).
4. **Distance from camera** — further from the camera renders earlier (i.e. behind). This is the tie-breaker Unity falls back to when Sorting Layer/Order in Layer/Render Queue are all equal, which is the default state for every sprite until explicitly changed — the practical effect: *"if you don't change these settings, Unity uses distance to camera as the first differentiator."* The exact distance calculation depends on the camera's projection, its **Transparency Sort Mode**, and the sprite's **Sprite Sort Point**.
5. **Shader/material grouping** — GameObjects sharing an identical shader+material batch together for draw-call efficiency, but relative order within that batch isn't guaranteed.

## Configuring Sorting Layers and Order in Layer

1. **Edit > Project Settings > Tags and Layers > Sorting Layers**, click **Add (+)** to create a layer. Layers listed lower render in front of layers listed higher — order the list deliberately, don't leave newly-added layers wherever they land.
2. On a `SpriteRenderer` (or other 2D renderer), set **Sorting Layer** and **Order in Layer** under Additional Settings — see [sprite-renderer.md](sprite-renderer.md). Every 2D GameObject starts on the **Default** layer with Order in Layer 0 until changed.

## Transparency Sort Mode / Axis (Camera)

On the `Camera` component, **Transparency Sort Mode** controls how distance-based sorting is computed for transparent objects: **Default** (perspective for a perspective camera, orthographic for an orthographic one), **Perspective**, **Orthographic**, or **Custom Axis** (sort along an explicit world-space axis — the standard setup for isometric or top-down games where "further from camera" isn't the same as "further along the Z axis").

## Sorting Group component

Groups a hierarchy of child renderers to sort as a single unit, so they can't get interleaved with another object's renderers even if individual children would otherwise sort differently by distance/layer.

| Property | Description |
|---|---|
| Sorting Layer | All child renderers render on this Sorting Layer while keeping their own relative order to each other. |
| Order in Layer | The group's own Order in Layer sublayer value. |
| Sorting Type | **Default** — sorts alongside sibling Sorting Groups at the same hierarchy level. **Sort at Root** — sorts at the top of the hierarchy, ignoring any parent Sorting Group. **Sort 3D as 2D** — sorts at the top level and ignores 3D GameObjects' Z value within the group, so mixed 2D/3D content sorts purely as 2D. |

Common use case: a character built from several stacked sprite parts (body, clothing, weapon, accessory) that must always render together as one visual unit, never interleaved with another character's parts even when both characters occupy similar depth.

## Practical guidance

- Don't rely on Z-position/distance-from-camera as the primary sorting mechanism for anything with an explicit design requirement (a UI element that must always be on top, a character that must always render behind a specific prop) — set an explicit Sorting Layer/Order in Layer instead; distance-based sorting is a fallback, not a design tool.
- For isometric/top-down 2D games, set the camera's **Transparency Sort Mode** to **Custom Axis** deliberately — the default perspective/orthographic distance sort produces visually wrong depth ordering for that camera angle.
- Reach for a **Sorting Group** the moment a multi-part object's pieces need to stay visually coherent as a unit — don't try to solve that with careful Order in Layer numbering alone, which breaks the first time another similar object's Order in Layer values overlap.
