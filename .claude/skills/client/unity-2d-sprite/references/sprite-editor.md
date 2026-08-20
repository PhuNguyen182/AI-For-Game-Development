# Sprite Editor — Slicing (Sprite Editor tab)

Sources: https://docs.unity3d.com/Manual/sprite/sprite-editor/use-editor.html, https://docs.unity3d.com/Manual/sprite/sprite-editor/sprite-editor-window-reference-landing.html, https://docs.unity3d.com/Manual/sprite/sprite-editor/sprite-editor-window-reference.html

## Opening the Sprite Editor

1. Select the texture asset in the Project window (not a scene object).
2. Confirm **Texture Type** is **Sprite (2D and UI)** in the Inspector (see [import-settings.md](import-settings.md)).
3. Click **Open Sprite Editor**.

## The module dropdown

The Sprite Editor window has a module dropdown in its toolbar, switching between:

| Module | Purpose | Covered in |
|---|---|---|
| Sprite Editor | Slice a texture into one or more sprites, edit each sprite rect's position/size/pivot/border. | This file |
| Custom Outline | Author the render mesh outline for each sprite. | [custom-outline.md](custom-outline.md) |
| Custom Physics Shape | Author the collision outline consumed by `Collider2D`'s "Use Sprite Physics Shape". | [custom-physics-shape.md](custom-physics-shape.md) |
| Secondary Textures | Attach normal-map/mask-map textures alongside the base sprite texture. | [secondary-textures.md](secondary-textures.md) |
| Skinning Editor | Bone rigging/weight painting for 2D Animation — belongs to the separate **2D Animation** package, out of scope for this skill. | N/A |

## Shared toolbar (present in every module)

| Control | Behavior |
|---|---|
| Preview | Toggles a live preview of pending changes in the Scene view. |
| Revert | Discards unsaved edits in the current module. |
| Apply | Commits edits back to the texture's import settings — nothing is saved until Apply is clicked. |
| Color | Toggles the texture display between full color and alpha-channel-only view — useful for judging outline/physics-shape tracing against transparency. |
| Zoom | Magnifies the canvas. |
| Mipmap Level | Slider to preview a specific mip level, when the texture has mipmaps. |

## Sprite Editor tab — slicing

| Control | Behavior |
|---|---|
| Slice dropdown | **Automatic** — segments sprites by transparent-pixel boundaries. **Grid By Cell Size** — uniform-size rects from a pixel size + offset + padding. **Grid By Cell Count** — divides the texture into a fixed column/row count. **Isometric Grid** — diamond-shaped rects with an "Is Alternate" staggering toggle, for isometric tile art. |
| Pixel Size / Column & Row | Size or count fields, shown depending on the chosen Slice type. |
| Offset / Padding | Pixel offset from the texture edge, and spacing left between generated sprite rects. |
| Keep Empty Rects | Preserves fully-transparent rects instead of discarding them (matters when a spritesheet's grid alignment depends on keeping "gap" frames, e.g. an animation sequence with blank frames). |
| Pivot / Pivot Unit Mode / Custom Pivot | Default pivot applied to every generated sprite rect — presets, Normalized (0–1) or Pixels unit mode, or explicit Custom X/Y. |
| Method | **Delete Existing** replaces all current sprite rects. **Smart** re-slices while trying to preserve existing rects' names/borders/pivots that still match. **Safe** only adds new rects, never touching existing ones. |
| Slice button | Executes the configured slice operation. |
| Trim | Resizes the selected sprite rect to fit tightly around its opaque pixels. |
| Locks dropdown (Multiple mode) | Locks specific fields (Name/Size/Position/Border/Create-Delete) so a subsequent re-slice doesn't disturb hand-tuned values. |

## Sprite Rect properties panel (per selected sprite)

| Field | Meaning |
|---|---|
| Name | The sub-sprite's identifier — this becomes its asset name, referenced by `Sprite.name` and by animation clips that key on frame name. |
| Position (X, Y, W, H) | The rect's location and size on the source texture, in pixels. |
| Border (L, R, T, B) | The 9-slice border in pixels — see [nine-slicing.md](nine-slicing.md). |
| Pivot / Pivot Unit Mode / Custom Pivot | Per-sprite override of the rotation/scale origin. |

## Practical guidance

- Use **Automatic** slicing only when sprites are cleanly separated by transparent padding on the sheet; a tightly-packed hand-authored sheet needs **Grid By Cell Size/Count** instead, or Automatic will merge adjacent sprites.
- Set **Method = Safe** when re-slicing a spritesheet that already has hand-tuned per-sprite borders/pivots and existing animation clips referencing sprite names by index/name — **Delete Existing** silently invalidates those references.
- Nothing is applied to the asset until **Apply** is clicked — closing the window or switching modules without applying discards the edit.
