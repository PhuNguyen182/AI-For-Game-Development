---
name: unity-2d-sprite
description: "2D sprites: import settings, Pixels Per Unit, Mesh Type, Sprite Editor slicing, SpriteRenderer, SpriteMask, sorting, SortingGroup, Sprite Atlas late binding, 9-slice. Use for sprite setup and 2D draw order."
user-invocable: false
---

# Unity 2D Sprite

Not for: `Rigidbody2D`/`Collider2D` (`unity-2d-physics`), `Light2D` (`unity-urp-rendering`), grid painting (`unity-tilemap`), spline geometry (`unity-2d-spriteshape`), sprite shaders (`shader-authoring`), animation clips (`unity-animation`), which sprite a state shows (`csharp-engineer`, Shared Core).
Docs: https://docs.unity3d.com/Manual/sprite/sprite-landing.html — unversioned, so confirm a setting or default against the project's Editor.

| Reference | Read when |
|---|---|
| [import-settings.md](references/import-settings.md) | Configuring a texture, or a sprite renders at the wrong world size |
| [sprite-editor.md](references/sprite-editor.md) | Slicing a sheet, authoring Custom Outline / Physics Shape / Secondary Textures, or normal/mask lighting has no effect |
| [sorting-sprites.md](references/sorting-sprites.md) | Two sprites draw in the wrong order |
| [sprite-renderer.md](references/sprite-renderer.md) | Wiring `SpriteRenderer`, 9-slicing, a `SpriteMask` that shows nothing, or measuring with the 2D Profiler |
| [sprite-atlas.md](references/sprite-atlas.md) | Cutting draw calls, shipping a smaller mobile texture set, or late-binding an atlas |
| [sprite-asset-reference.md](references/sprite-asset-reference.md) | Reading `Sprite` data from code, or blocking out with placeholder sprites |

## Steps
1. **Settle Pixels Per Unit against the existing visual set first** — PPU fixes rendered size and the scale of the sprite-derived physics shape, so a mismatch is an art bug and a hitbox bug at once. See import-settings.md.
2. **Pick Mesh Type by 9-slicing, not overdraw instinct** — Full Rect is mandatory for 9-slicing, and Unity forces Full Rect under 32×32, so Tight on small icons changes nothing. Use Tight only on a large sprite with heavy transparent padding, then trim with Custom Outline.
3. **Slice a sheet that already has references with Method Safe or Smart**; Delete Existing only for a first slice or a deliberate re-cut. Nothing is written until Apply.
4. **Author collision geometry once on the `Sprite` asset, not per instance**; lower Outline Detail to the coarsest silhouette that plays correctly. A roughly convex silhouette needs only a Box/Circle collider (`unity-2d-physics`).
5. **Name secondary textures exactly `_NormalMap` / `_MaskTex`** — flat normal-mapped sprites are usually this.
6. **Set Sorting Layer and Order in Layer for every stated depth relationship**; add a `SortingGroup` when a multi-part object must stay uninterleaved; use Transparency Sort Mode Custom Axis for isometric/top-down cameras.
7. **Use 9-slicing or `SpriteMask` only when the design resizes or reveals**: Sliced for smooth frames, Tiled for patterns. A mask that does nothing: check Depth/Stencil Buffer on the active 2D Renderer Data first, then Mask Interaction on the target.
8. **Group an atlas by what is on screen together** — an atlas is resident as a unit. Turn Allow Rotation and Tight Packing off for sprites that Sprite Shape or UI `Image` re-mesh; ship a lower-scale Variant, not a duplicate Master.
9. **Keep decisions out of the sprite layer** — Core resolves the state; client code only assigns the resolved `sprite`/`color`/sorting value, and only on change.
10. **Read sprite data through members valid under packing** (`rect`, `bounds`, not `textureRect`). When real art replaces a placeholder, redo steps 1-2.
11. **Confirm any draw-call or overdraw claim in the Profiler 2D module** before reporting it; Usage % per atlas is the evidence.
12. **Symptom ambiguous between import, material and lighting ("too dark")** → say which layer is assumed and confirm before editing shared assets.

## Never
- Re-slice a referenced sheet with Delete Existing — clips and prefabs resolving sprites by name break with no console error.
- Use Force Generate All (Custom Outline / Physics Shape) as a routine re-sync — it overwrites hand-edited geometry across the sheet and cannot be undone after Apply; confirm with the requester in this conversation first.
- Depend on distance-from-camera for a stated depth requirement — it is the last tie-breaker and changes when anything moves in Z.
- Mirror with negative Transform scale — use Flip X/Y; negative scale also inverts child colliders.
- Assume an atlas-fetched sprite equals a scene-authored one — `SpriteAtlas.GetSprite` returns a clone per call (allocates, fails `==`).
- Ship a Master and its Variant both with Include in Build on — which resolves is non-deterministic; disable it on the Master.

## Output
```
## 2D Sprite Work — <asset/feature>
- Import: Sprite Mode, PPU <n> (matched to <set>), Mesh Type, Generate Physics Shape, platform overrides
- Sprite Editor: modules used, slice Method, key settings
- Sorting: Sorting Layer, Order in Layer, Transparency Sort Mode, SortingGroup <why>
- 9-slice / mask: Border L,R,T,B, Draw Mode, Mask Interaction, Depth/Stencil confirmed
- Atlas: Master/Variant, grouping rationale, Allow Rotation + Tight Packing, Include in Build, late binding
- Verification: 2D Profiler counts and Usage %, or "not yet measured"
- Known limitations: <...>
```

## Example
- "One big atlas for every sprite, fewer draw calls" → declined: batching is per atlas texture and material, so co-visible grouping already gets the draw-call floor, while one atlas stays wholly resident for any scene using one sprite. Packed per co-visibility (HUD atlas, one per character set) with a 0.5-scale Variant for mobile; measured Usage % per atlas.
