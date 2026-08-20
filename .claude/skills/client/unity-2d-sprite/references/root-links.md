# Root Reference Links — Unity 2D Sprite

Root Manual landing pages for Unity's built-in 2D Sprite authoring pipeline (`UnityEngine.Sprite`, `UnityEngine.SpriteRenderer`, `UnityEngine.U2D.*`). Each row's "Covered in" column points to the reference file that expands that topic with full Inspector/Scripting API detail.

| Topic | URL | Covered in |
|---|---|---|
| Sprites landing | https://docs.unity3d.com/Manual/sprite/sprite-landing.html | (this file) |
| Add placeholder sprites | https://docs.unity3d.com/Manual/sprite/placeholder/placeholder-landing.html | [placeholder-sprites.md](placeholder-sprites.md) |
| Import a sprite or spritesheet texture | https://docs.unity3d.com/Manual/sprite/import-images-sprites/import-images-sprites-landing.html | [import-settings.md](import-settings.md) |
| Sprite (2D and UI) import settings reference | https://docs.unity3d.com/Manual/texture-type-sprite.html | [import-settings.md](import-settings.md) |
| Cut out sprites from a texture (Sprite Editor tab) | https://docs.unity3d.com/Manual/sprite/sprite-editor/use-editor.html | [sprite-editor.md](sprite-editor.md) |
| Sprite Editor window reference (landing) | https://docs.unity3d.com/Manual/sprite/sprite-editor/sprite-editor-window-reference-landing.html | [sprite-editor.md](sprite-editor.md) |
| Sprite Editor tab reference | https://docs.unity3d.com/Manual/sprite/sprite-editor/sprite-editor-window-reference.html | [sprite-editor.md](sprite-editor.md) |
| Crop a sprite (Custom Outline) | https://docs.unity3d.com/Manual/sprite/sprite-editor/generate-outline.html | [custom-outline.md](custom-outline.md) |
| Custom Outline tab reference | https://docs.unity3d.com/Manual/sprite/sprite-editor/custom-outline-editor-reference.html | [custom-outline.md](custom-outline.md) |
| Create collision shapes for a sprite | https://docs.unity3d.com/Manual/sprite/create-collision-geometry.html | [custom-physics-shape.md](custom-physics-shape.md) |
| Custom Physics Shape tab reference | https://docs.unity3d.com/Manual/sprite/sprite-editor/custom-physics-shape-editor-reference.html | [custom-physics-shape.md](custom-physics-shape.md) |
| Secondary Textures tab reference | https://docs.unity3d.com/Manual/sprite/sprite-editor/secondary-textures-editor-reference.html | [secondary-textures.md](secondary-textures.md) |
| Sorting sprites (landing) | https://docs.unity3d.com/Manual/sprite/sort-sprites/sort-sprites-landing.html | [sorting-sprites.md](sorting-sprites.md) |
| 2D rendering order | https://docs.unity3d.com/Manual/sprite/sort-sprites/sort-sprites.html | [sorting-sprites.md](sorting-sprites.md) |
| Change the sorting order of 2D GameObjects | https://docs.unity3d.com/Manual/2d-renderer-sorting.html | [sorting-sprites.md](sorting-sprites.md) |
| Sorting Group component reference | https://docs.unity3d.com/Manual/sprite/sorting-group/sorting-group-reference.html | [sorting-sprites.md](sorting-sprites.md) |
| Scaling sprites dynamically using 9-slicing (landing) | https://docs.unity3d.com/Manual/sprite/9-slice/9-slice-landing.html | [nine-slicing.md](nine-slicing.md) |
| 9-slicing (concept) | https://docs.unity3d.com/Manual/sprite/9-slice/9-slicing.html | [nine-slicing.md](nine-slicing.md) |
| 9-slice a sprite (workflow) | https://docs.unity3d.com/Manual/sprite/9-slice/set-sprite-9slicing.html | [nine-slicing.md](nine-slicing.md) |
| Masking sprites (landing) | https://docs.unity3d.com/Manual/sprite/mask/mask-landing.html | [sprite-mask.md](sprite-mask.md) |
| Add a sprite mask | https://docs.unity3d.com/Manual/sprite/mask/hide-reveal-parts-sprite-mask.html | [sprite-mask.md](sprite-mask.md) |
| Sprite Mask component reference | https://docs.unity3d.com/Manual/sprite/mask/sprite-mask-reference.html | [sprite-mask.md](sprite-mask.md) |
| Packing sprites into a sprite atlas (landing) | https://docs.unity3d.com/Manual/sprite/atlas/atlas-landing.html | [sprite-atlas.md](sprite-atlas.md) |
| Create a sprite atlas | https://docs.unity3d.com/Manual/sprite/atlas/create-sprite-atlas.html | [sprite-atlas.md](sprite-atlas.md) |
| Master/variant sprite atlases | https://docs.unity3d.com/Manual/sprite/atlas/master-variant/master-variant-sprite-atlases.html | [sprite-atlas.md](sprite-atlas.md) |
| Runtime loading (late binding) | https://docs.unity3d.com/Manual/sprite/atlas/distribution/load-sprite-atlas-spriteatlasmanageratlasrequested.html | [sprite-atlas.md](sprite-atlas.md) |
| Sprite Atlas Inspector reference | https://docs.unity3d.com/Manual/sprite/atlas/sprite-atlas-reference.html | [sprite-atlas.md](sprite-atlas.md) |
| Sprite asset reference | https://docs.unity3d.com/Manual/class-Sprite.html | [sprite-asset-reference.md](sprite-asset-reference.md) |
| Sprite Renderer component reference | https://docs.unity3d.com/Manual/sprite/renderer/sprite-renderer-reference.html | [sprite-renderer.md](sprite-renderer.md) |
| 2D Profiler module reference | https://docs.unity3d.com/Manual/sprite/profiler-2d.html | [sprite-renderer.md](sprite-renderer.md) (Performance note) |

## Parent context

| Page | URL |
|---|---|
| 2D game development overview | https://docs.unity3d.com/Manual/Unity2D.html |
| Convert 2D assets from Built-In Render Pipeline to URP | https://docs.unity3d.com/Manual/urp-2d-convert-assets.html |
| Set up your project for 2D games | https://docs.unity3d.com/Manual/setup-project-2d-game.html |

## Scripting API — namespace roots

| Member | Description |
|---|---|
| `UnityEngine.Sprite` | The sprite asset itself — texture region, pivot, border, physics shape, mesh geometry. See [sprite-asset-reference.md](sprite-asset-reference.md). |
| `UnityEngine.SpriteRenderer` | Component that draws a `Sprite` in a scene. See [sprite-renderer.md](sprite-renderer.md). |
| `UnityEngine.U2D.SpriteAtlas` | Runtime handle to a packed sprite atlas asset. See [sprite-atlas.md](sprite-atlas.md). |
| `UnityEngine.U2D.SpriteAtlasManager` | Static class exposing the `atlasRequested` event for late-binding atlases excluded from the build. See [sprite-atlas.md](sprite-atlas.md). |

For 2D physics simulation built on top of a sprite's physics shape (`Rigidbody2D`, `Collider2D`, joints, effectors), see the sibling `unity-2d-physics` skill. For URP 2D Lighting (`Light2D`, 2D Renderer Data, normal/mask secondary textures consumed at runtime), see `unity-urp-rendering`. For Tilemap and Sprite Shape (separate authoring systems built on top of sprites), no dedicated skill exists yet in this project — treat as out of scope and flag explicitly.
