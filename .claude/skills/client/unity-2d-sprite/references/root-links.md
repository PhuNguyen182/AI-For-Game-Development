# Root Links — Unity Built-in 2D Sprite Pipeline

Source: the Unity Manual section roots listed below, as provided for this skill.
Covers: the whole skill — provenance and version anchor for every file in this folder.

Anchors every link in this folder to Unity's core Manual, whose URLs carry no
version segment and therefore always resolve to the currently published
Manual. That is the pin: re-verify a page against the project's installed
Editor/LTS version whenever a setting's presence or default matters, because
an unversioned URL silently follows Unity forward. Anything not reachable
under a root below is out of scope for this skill, not merely undocumented
here — 2D physics simulation, `Light2D`, Tilemap, and Sprite Shape each have
their own skill.

| Root | Holds | Source |
|---|---|---|
| Sprites section | Every topic this skill covers, as a table of contents | [Sprites](https://docs.unity3d.com/Manual/sprite/sprite-landing.html) |
| Sprite import settings | Texture Type Sprite and its full settings reference | [Sprite (2D and UI) import settings](https://docs.unity3d.com/Manual/texture-type-sprite.html) |
| Sprite Editor window | All four authoring modules and their toolbars | [Sprite Editor window reference](https://docs.unity3d.com/Manual/sprite/sprite-editor/sprite-editor-window-reference-landing.html) |
| Sorting | The 2D draw-order chain and Sorting Group | [Sorting sprites](https://docs.unity3d.com/Manual/sprite/sort-sprites/sort-sprites-landing.html) |
| Sprite Atlas | Packing, Master/Variant, runtime binding | [Packing sprites into a sprite atlas](https://docs.unity3d.com/Manual/sprite/atlas/atlas-landing.html) |
| Project setup | 2D template and Built-in→URP asset conversion | [Set up your project for 2D games](https://docs.unity3d.com/Manual/setup-project-2d-game.html) |

## Topic → file map

| Topic | File | Source |
|---|---|---|
| Import settings, PPU, Mesh Type, compression | [import-settings.md](import-settings.md) | [Import images as sprites](https://docs.unity3d.com/Manual/sprite/import-images-sprites/import-images-sprites-landing.html) |
| Slicing a spritesheet | [sprite-editor.md](sprite-editor.md) | [Cut out sprites from a texture](https://docs.unity3d.com/Manual/sprite/sprite-editor/use-editor.html) |
| Render-mesh outline | [custom-outline.md](custom-outline.md) | [Custom Outline tab reference](https://docs.unity3d.com/Manual/sprite/sprite-editor/custom-outline-editor-reference.html) |
| Collision outline on the sprite asset | [custom-physics-shape.md](custom-physics-shape.md) | [Create collision shapes for a sprite](https://docs.unity3d.com/Manual/sprite/create-collision-geometry.html) |
| Normal/mask secondary textures | [secondary-textures.md](secondary-textures.md) | [Secondary Textures tab reference](https://docs.unity3d.com/Manual/sprite/sprite-editor/secondary-textures-editor-reference.html) |
| Draw order, Sorting Group, sort axis | [sorting-sprites.md](sorting-sprites.md) | [2D rendering order](https://docs.unity3d.com/Manual/sprite/sort-sprites/sort-sprites.html) |
| Border and Draw Mode resizing | [nine-slicing.md](nine-slicing.md) | [9-slicing sprites](https://docs.unity3d.com/Manual/sprite/9-slice/9-slice-landing.html) |
| Stencil-based reveal/hide | [sprite-mask.md](sprite-mask.md) | [Masking sprites](https://docs.unity3d.com/Manual/sprite/mask/mask-landing.html) |
| Atlas packing and late binding | [sprite-atlas.md](sprite-atlas.md) | [Create a sprite atlas](https://docs.unity3d.com/Manual/sprite/atlas/create-sprite-atlas.html) |
| Renderer component and 2D Profiler | [sprite-renderer.md](sprite-renderer.md) | [Sprite Renderer component reference](https://docs.unity3d.com/Manual/sprite/renderer/sprite-renderer-reference.html) |
| `Sprite` runtime data | [sprite-asset-reference.md](sprite-asset-reference.md) | [Sprite asset reference](https://docs.unity3d.com/Manual/class-Sprite.html) |
| Built-in blockout shapes | [placeholder-sprites.md](placeholder-sprites.md) | [Add placeholder sprites](https://docs.unity3d.com/Manual/sprite/placeholder/placeholder-landing.html) |

Every other link in this `references/` folder is a specific page under these
roots. Because Unity publishes the core Manual unversioned, treat any default
value or Inspector field name quoted in this folder as "current at authoring
time" and confirm it against the Editor the project actually builds with.
