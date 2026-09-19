# Sprite Editor — Slicing, Modules & the Apply Contract

Sources: [Cut out sprites from a texture](https://docs.unity3d.com/Manual/sprite/sprite-editor/use-editor.html), [Sprite Editor window reference](https://docs.unity3d.com/Manual/sprite/sprite-editor/sprite-editor-window-reference.html).
Covers: SKILL.md §4 — **"Slice with Method Safe or Smart on any sheet that already has references"**.

The Sprite Editor edits a texture's *import settings*, not a scene object, so
its output is shared by every instance of every sprite it cuts. That is why
the slice Method matters: a re-slice can invalidate references held elsewhere
in the project. Open it by selecting the texture, confirming Texture Type is
Sprite (2D and UI) per [import-settings.md](import-settings.md), and clicking
**Open Sprite Editor**.

## Modules

| Module | What it authors | Source |
|---|---|---|
| Sprite Editor | Sprite rects, names, pivots, and 9-slice borders — this file | [Sprite Editor tab reference](https://docs.unity3d.com/Manual/sprite/sprite-editor/sprite-editor-window-reference.html) |
| Custom Outline | The render mesh, effective only at Mesh Type Tight — see [custom-outline.md](custom-outline.md) | [Custom Outline tab reference](https://docs.unity3d.com/Manual/sprite/sprite-editor/custom-outline-editor-reference.html) |
| Custom Physics Shape | The collision outline stored on the sprite — see [custom-physics-shape.md](custom-physics-shape.md) | [Custom Physics Shape tab reference](https://docs.unity3d.com/Manual/sprite/sprite-editor/custom-physics-shape-editor-reference.html) |
| Secondary Textures | Normal/mask maps bound by name — see [secondary-textures.md](secondary-textures.md) | [Secondary Textures tab reference](https://docs.unity3d.com/Manual/sprite/sprite-editor/secondary-textures-editor-reference.html) |
| Skinning Editor | 2D bone rigging — ships with the separate 2D Animation package and is outside this skill | [Sprite Editor window reference](https://docs.unity3d.com/Manual/sprite/sprite-editor/sprite-editor-window-reference-landing.html) |

## Shared toolbar

| Control | What it decides | Source |
|---|---|---|
| Apply / Revert | Nothing reaches the asset until Apply — closing the window or switching modules discards pending edits without warning | [Sprite Editor window reference](https://docs.unity3d.com/Manual/sprite/sprite-editor/sprite-editor-window-reference.html) |
| Color | Switches the canvas to alpha-only view, which is how an outline or physics shape is judged against real transparency rather than against art | [Sprite Editor window reference](https://docs.unity3d.com/Manual/sprite/sprite-editor/sprite-editor-window-reference.html) |
| Preview | Shows pending changes live in the Scene view before Apply commits them | [Sprite Editor window reference](https://docs.unity3d.com/Manual/sprite/sprite-editor/sprite-editor-window-reference.html) |
| Zoom / Mipmap Level | Canvas magnification, and previewing a specific mip when the texture has them | [Sprite Editor window reference](https://docs.unity3d.com/Manual/sprite/sprite-editor/sprite-editor-window-reference.html) |

## Slicing

| Control | What it decides | Source |
|---|---|---|
| Slice type | **Automatic** segments by transparent-pixel boundaries and merges any sprites that touch; **Grid By Cell Size** and **Grid By Cell Count** are the only safe choices on a tightly packed sheet; **Isometric Grid** cuts diamonds with an Is Alternate stagger | [Sprite Editor tab reference](https://docs.unity3d.com/Manual/sprite/sprite-editor/sprite-editor-window-reference.html) |
| Method | **Delete Existing** rebuilds every rect and breaks any clip or prefab resolving a sprite by name; **Smart** re-slices while preserving still-matching names, borders, and pivots; **Safe** only adds new rects | [Sprite Editor tab reference](https://docs.unity3d.com/Manual/sprite/sprite-editor/sprite-editor-window-reference.html) |
| Keep Empty Rects | Preserves fully transparent cells — required when an animation's timing depends on blank frames holding their grid position | [Sprite Editor tab reference](https://docs.unity3d.com/Manual/sprite/sprite-editor/sprite-editor-window-reference.html) |
| Offset / Padding | Pixel offset from the texture edge and spacing between generated rects — the two values that fix a grid slice landing one pixel off | [Sprite Editor tab reference](https://docs.unity3d.com/Manual/sprite/sprite-editor/sprite-editor-window-reference.html) |
| Pivot / Pivot Unit Mode | Default pivot applied to every generated rect, in Normalized or Pixels units | [Sprite Editor tab reference](https://docs.unity3d.com/Manual/sprite/sprite-editor/sprite-editor-window-reference.html) |
| Locks (Multiple mode) | Locks Name/Size/Position/Border/Create-Delete so a later re-slice cannot disturb hand-tuned values — the durable version of choosing Safe once | [Sprite Editor tab reference](https://docs.unity3d.com/Manual/sprite/sprite-editor/sprite-editor-window-reference.html) |
| Trim | Shrinks the selected rect to its opaque pixels | [Sprite Editor tab reference](https://docs.unity3d.com/Manual/sprite/sprite-editor/sprite-editor-window-reference.html) |

## Per-sprite rect fields

| Field | What it decides | Source |
|---|---|---|
| Name | Becomes the sub-sprite's asset name and the key animation clips resolve frames by — renaming it breaks those bindings silently | [Sprite Editor tab reference](https://docs.unity3d.com/Manual/sprite/sprite-editor/sprite-editor-window-reference.html) |
| Position (X, Y, W, H) | The rect on the source texture, in pixels | [Sprite Editor tab reference](https://docs.unity3d.com/Manual/sprite/sprite-editor/sprite-editor-window-reference.html) |
| Border (L, R, T, B) | The 9-slice border — see [nine-slicing.md](nine-slicing.md) | [9-slice a sprite](https://docs.unity3d.com/Manual/sprite/9-slice/set-sprite-9slicing.html) |
| Pivot / Custom Pivot | Per-sprite override of the rotation and scale origin | [Sprite Editor tab reference](https://docs.unity3d.com/Manual/sprite/sprite-editor/sprite-editor-window-reference.html) |
