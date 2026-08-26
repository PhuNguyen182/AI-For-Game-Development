---
name: unity-2d-sprite
description: >
  Unity built-in 2D Sprite authoring — `Sprite`, `SpriteRenderer`,
  `SpriteMask`, `SortingGroup`, `SpriteAtlas`, `SpriteAtlasManager`.
  Covers import settings (Sprite Mode, Pixels Per Unit, Mesh Type Full
  Rect vs Tight, Generate Physics Shape), the Sprite Editor's slicing,
  Custom Outline, Custom Physics Shape and Secondary Textures modules,
  Sorting Layer, Order in Layer, Transparency Sort Mode, Draw Mode
  Sliced/Tiled 9-slicing, Mask Interaction, and atlas packing. Use when a
  sprite renders wrong, sorts wrong, or costs too many draw calls.
  Not for: `Rigidbody2D`/`Collider2D` dynamics (`unity-2d-physics`),
  `Light2D` setup (`unity-urp-rendering`), grid-cell painting
  (`unity-tilemap`), spline level geometry (`unity-2d-spriteshape`),
  sprite shaders (`shader-authoring`), animation clips
  (`unity-animation`), which sprite to show (`csharp-engineer`).
---

# Unity 2D Sprite — Import, Sprite Editor, Sorting, Masking & Atlas Packing

## Bundled resources

### References

| File | Contents | Read when |
|---|---|---|
| [root-links.md](references/root-links.md) | Manual/API roots this skill is pinned to, and the topic→file map | Starting any sprite task, or checking whether a page is in scope |
| [import-settings.md](references/import-settings.md) | Texture Type, Sprite Mode, PPU, Mesh Type, Pivot, compression | Configuring a texture, or a sprite renders at the wrong world size |
| [sprite-editor.md](references/sprite-editor.md) | Slice types, Method Safe/Smart/Delete Existing, rect fields | Cutting a spritesheet, or a re-slice broke existing references |
| [custom-outline.md](references/custom-outline.md) | Render-mesh outline authoring and Outline Detail cost | A Tight sprite has heavy transparent padding to trim |
| [custom-physics-shape.md](references/custom-physics-shape.md) | Collision-outline authoring stored on the `Sprite` asset | A collider must follow the sprite silhouette |
| [secondary-textures.md](references/secondary-textures.md) | `_NormalMap`/`_MaskTex` attachment and the name-binding rule | Sprite normal/mask lighting shows no effect |
| [sorting-sprites.md](references/sorting-sprites.md) | The five-step sort chain, Sorting Group, Transparency Sort Mode | Two sprites draw in the wrong order |
| [nine-slicing.md](references/nine-slicing.md) | Border authoring, Sliced vs Tiled, Continuous vs Adaptive | A sprite must resize without distorting its corners |
| [sprite-mask.md](references/sprite-mask.md) | `SpriteMask` properties, Custom Range, stencil prerequisite | A mask reveals or hides nothing |
| [sprite-atlas.md](references/sprite-atlas.md) | Packing settings, Master/Variant, `atlasRequested` late binding | Cutting draw calls, or shipping a smaller mobile texture set |
| [sprite-renderer.md](references/sprite-renderer.md) | Inspector fields, scripting surface, the 2D Profiler module | Wiring or measuring the renderer component |
| [sprite-asset-reference.md](references/sprite-asset-reference.md) | `Sprite` runtime data — `rect`, `bounds`, `border`, physics shape | Reading sprite data from code |
| [placeholder-sprites.md](references/placeholder-sprites.md) | Built-in primitive sprites and the swap-to-final-art path | Blocking out a scene before art exists |

## 1. Objective
Make a sprite render at the intended size, in the intended order, with the intended collision and lighting data attached, and at a draw-call cost the target platform can afford — without the silent failures this pipeline specialises in: a Mesh Type that a small texture overrides, a secondary texture whose name nothing binds, a mask with no stencil buffer to write into, a re-slice that invalidates every clip referencing the old sprite names, and an atlas resident in memory for content that is never on screen.

## 2. Role
Act as the built-in 2D Sprite authoring specialist for the client track — the skill reached for whenever a `Sprite`, `SpriteRenderer`, `SpriteMask`, `SortingGroup`, or `SpriteAtlas` must be configured, or whenever a sprite's on-screen result does not match what the art or design intended.

## 3. When to invoke this skill
- Setting a texture's Sprite import settings — Sprite Mode, Pixels Per Unit, Mesh Type, Pivot, Extrude Edges, Generate Physics Shape, or per-platform compression.
- Slicing a spritesheet, or authoring Custom Outline / Custom Physics Shape / Secondary Textures in the Sprite Editor.
- A sorting symptom: sprites interleaving with another object's parts, isometric depth reading backwards, a prop drawing over a character it should sit behind.
- A 9-slicing, `SpriteMask`, or `SpriteRenderer` configuration task, including Draw Mode and Mask Interaction.
- Packing or late-binding a `SpriteAtlas`, or cutting sprite draw calls.
- Reading `Sprite` data from code — `rect`, `bounds`, `border`, `GetPhysicsShape`.
- Negative trigger: `Rigidbody2D`, `Collider2D`, joint, or effector configuration — that's `unity-2d-physics`; this skill only authors the shape geometry those components consume.
- Negative trigger: `Light2D` or 2D Renderer Data setup, even though it consumes this skill's secondary textures — that's `unity-urp-rendering`.
- Negative trigger: painting a level from tiles on a grid — that's `unity-tilemap`.
- Negative trigger: spline-based level geometry that tiles sprites along an outline — that's `unity-2d-spriteshape`.
- Negative trigger: writing or modifying the shader on a sprite material — that's `shader-authoring`.
- Negative trigger: authoring animation clips that key sprite frames, or the Animator driving them — that's `unity-animation`.
- Negative trigger: deciding *which* sprite, tint, or visibility a game state should produce — that's `csharp-engineer`'s Shared Core, per `coding-principles.md`'s Shared Core integrity section.

## 4. How to use this skill
1. **Settle Pixels Per Unit against the existing visual set before anything else**, per [import-settings.md](references/import-settings.md) — PPU fixes both the sprite's rendered world size and the scale of the physics shape derived from it, so a mismatch inside one set is simultaneously an art bug and a hitbox bug, and every later decision is measured against it; [root-links.md](references/root-links.md) pins the doc version each setting below is described at.
2. **Pick Mesh Type by whether the sprite is 9-sliced, not by overdraw instinct** — Full Rect is mandatory for 9-slicing, and Unity forces Full Rect on any sprite under 32×32 regardless of the setting, so choosing Tight to save fill on small icons changes nothing. Choose Tight only for a large sprite with genuinely heavy transparent padding, then trim it with [custom-outline.md](references/custom-outline.md).
3. **Slice with Method Safe or Smart on any sheet that already has references** ([sprite-editor.md](references/sprite-editor.md)) — Delete Existing rebuilds every rect and silently breaks animation clips and prefab fields that resolve sprites by name. Delete Existing is for a first slice or a deliberate re-cut, and nothing is written to the asset until Apply.
4. **Author collision geometry once on the `Sprite` asset, never per instance**, per [custom-physics-shape.md](references/custom-physics-shape.md) — a shape stored on the sprite is reused by every GameObject referencing it. Tune Outline Detail down to the lowest silhouette that still reads: vertex count is paid per collision check, per `performance-and-algorithms.md`'s simplest-collider-shape guidance.
5. **Name a secondary texture exactly `_NormalMap` or `_MaskTex`**, per [secondary-textures.md](references/secondary-textures.md) — the URP 2D lit shaders look up those property names and nothing else; a custom name attaches the texture, raises no error, and produces no lighting. This is the first thing to check when normal-mapped sprites look flat.
6. **Set Sorting Layer and Order in Layer explicitly for every depth relationship the design states**, per [sorting-sprites.md](references/sorting-sprites.md) — distance-from-camera is only the tie-breaker Unity falls back to once layer, order, and render queue are all equal, so an unconfigured scene sorts by an axis nobody chose. Add a `SortingGroup` the moment a multi-part object must stay uninterleaved, and set Transparency Sort Mode to Custom Axis for isometric or top-down cameras.
7. **Reach for 9-slicing or `SpriteMask` only when the design actually resizes or reveals something** ([nine-slicing.md](references/nine-slicing.md), [sprite-mask.md](references/sprite-mask.md)) — Sliced for smooth frames, Tiled for repeating pattern. Masking is stencil-based, so confirm the active 2D Renderer Data has Depth/Stencil Buffer enabled before debugging anything else; that setting is the usual reason a mask does nothing.
8. **Group an atlas by what appears on screen together**, per [sprite-atlas.md](references/sprite-atlas.md) — an atlas mixing unrelated content stays wholly resident for a scene using a fraction of it. Turn Allow Rotation and Tight Packing off for sprites a downstream system re-meshes (Sprite Shape, UI `Image`), ship a lower-resolution Variant instead of a duplicated Master, and subscribe `SpriteAtlasManager.atlasRequested` with a named method unsubscribed in `OnDisable`, per `coding-principles.md`'s Event handlers section.
9. **Keep the sprite layer free of decisions**, per `coding-principles.md`'s Shared Core integrity section — `Game.Core.*` resolves which state is active; [sprite-renderer.md](references/sprite-renderer.md) code only assigns the already-resolved `sprite`, `color`, or sorting value, and only when it actually changed.
10. **Read sprite data through the members that stay valid under packing** ([sprite-asset-reference.md](references/sprite-asset-reference.md)) — `rect` and `bounds` hold regardless of atlas state, while `textureRect` throws on a tightly packed sprite. When art has not landed yet, block out with [placeholder-sprites.md](references/placeholder-sprites.md) and re-settle the Pixels Per Unit and Mesh Type decisions when the real texture arrives.
11. **Confirm any draw-call or overdraw claim with the Profiler's 2D module before reporting it**, per `performance-and-algorithms.md`'s Verification section — its Usage percentage per atlas is the evidence that packing helped; asserting a batching win from the atlas count alone is not.
12. **When the requested visual result is ambiguous about ownership, state the boundary and ask** — "sprite is too dark" can be import gamma, a material, or a `Light2D` rig, and the three route to three different owners; name which one is being assumed rather than silently picking.

## 5. Specific goals / tasks this skill performs
- Sprite texture import configuration, including per-platform compression and Max Size overrides.
- Spritesheet slicing and per-sprite rect, pivot, and border authoring.
- Custom Outline (render mesh) and Custom Physics Shape (collision outline) authoring.
- Secondary texture attachment for downstream 2D lighting.
- Sorting Layer, Order in Layer, Transparency Sort Mode, and `SortingGroup` setup.
- 9-slicing setup and `SpriteMask` configuration, including Custom Range scoping.
- Sprite Atlas packing, Master/Variant sizing, and `atlasRequested` late binding.
- `SpriteRenderer` wiring and `Sprite` scripting-API reads.
- Out of scope: 2D physics simulation (`unity-2d-physics`), 2D lighting (`unity-urp-rendering`), tile painting (`unity-tilemap`), spline geometry (`unity-2d-spriteshape`), sprite shaders (`shader-authoring`), animation clips (`unity-animation`), gameplay state driving visuals (`csharp-engineer`).

## 6. Output format
```
## 2D Sprite Work — <asset/feature name>
- Import: Sprite Mode <Single/Multiple/Polygon>, PPU <n> (matched to <set>), Mesh Type <Full Rect/Tight>, Generate Physics Shape <yes/no>, platform overrides <summary>
- Sprite Editor: module(s) <Slicing/Custom Outline/Custom Physics Shape/Secondary Textures>, slice Method <Safe/Smart/Delete Existing>, key settings
- Sorting: Sorting Layer <name>, Order in Layer <n>, Transparency Sort Mode <mode/axis>, SortingGroup <yes/no + why>
- 9-slicing / mask: Border <L,R,T,B>, Draw Mode <Simple/Sliced/Tiled>, Mask Interaction <mode>, Depth/Stencil confirmed <yes/no/not applicable>
- Atlas: Master/Variant <n>, grouping rationale, Allow Rotation + Tight Packing <on/off + why>, Include in Build <yes/no>, late binding <yes/no>
- Shared Core boundary: <what Core decides vs what this layer renders>
- Verification: 2D Profiler <sprite/atlas counts, Usage %>, or "not yet measured"
- Layer: Game.Client.* / Editor-only (import settings are asset metadata)
- Known limitations: <...>
```

**Extended report — emit ONLY when the requester asks for it.** It replaces the one-line `Known limitations` above with all three fields:
```
- Known limitations: <what the delivered solution does not cover — omit this line entirely if there are genuinely none>
- Latent concerns: <failure modes not yet triggered: assumptions that hold only under current conditions, thresholds not yet reached, trade-offs knowingly deferred>
- Future remediation: <the concrete fix for each concern above, each with the condition that should trigger it>
```

## 7. Examples
**Example 1**
- Input: "This 8-frame walk cycle imports fine but the character is twice the size of everyone else, and its hitbox is way off."
- Output: one cause, not two — PPU was left at the 100 default while the rest of the character set uses 32, so both the rendered size and the sprite-derived physics shape scaled by the same factor. Set PPU to 32, Sprite Mode Multiple, Mesh Type Tight (frames carry wide transparent margins and are well over 32×32), re-sliced with Grid By Cell Size using Method Smart so the existing clip's frame names survived, then authored one Custom Physics Shape at low Outline Detail rather than accepting the auto-generated outline. Hand-off: the `Collider2D`/`Rigidbody2D` consuming that shape → `unity-2d-physics`; the clip playback → `unity-animation`.

**Example 2**
- Input: "Just put every sprite in the game into one big atlas — fewer atlases means fewer draw calls."
- Output: declined. Batching is per-atlas-texture *and* per-material, so one oversized atlas does not reduce draw calls below what co-visible grouping already achieves, and it forces the whole combined texture resident for any scene touching a single sprite in it — the memory-footprint failure `performance-and-algorithms.md`'s Assets & memory footprint section describes. Packed instead by co-visibility (one HUD atlas, one per character set), with a 0.5-scale Variant for mobile, and measured the result in the Profiler's 2D module: Usage per resident atlas is the number that decides whether a grouping is right.

**Example 3**
- Input: "Normal maps are attached to the tileset sprites but the 2D lights do nothing to them."
- Output: the secondary textures had been named `Normal` rather than `_NormalMap`, so the URP 2D lit shader found no such property, bound nothing, and logged nothing. Renamed both entries to `_NormalMap`/`_MaskTex` and re-applied, then verified every sprite in the shared atlas carries a matching secondary-texture count, since a mismatch inside one atlas fails at pack time. Hand-off: the `Light2D` rig and 2D Renderer Data setup itself → `unity-urp-rendering`.

## 8. Edge cases & guardrails
- Never treat Mesh Type = Tight as an overdraw fix on small sprites — Unity forces Full Rect under 32×32, so the setting reads as applied while nothing changed.
- Never re-slice a referenced spritesheet with Method = Delete Existing — clips and prefabs resolving sprites by name break silently, with no console error to trace back.
- Never leave a secondary texture under a custom name and assume the shader will find it — `_NormalMap`/`_MaskTex` are the only names the built-in 2D lit shaders look up.
- Never rely on distance-from-camera for a stated depth requirement — it is the last tie-breaker in the chain, so it changes the moment anything moves in Z.
- Never use Force Generate All in Custom Outline or Custom Physics Shape as a routine re-sync — it overwrites hand-edited geometry across the whole sheet and cannot be undone after Apply; confirm with the requester in the current conversation first.
- Never mirror a sprite with a negative Transform scale — use Flip X/Y, since negative scale also inverts child colliders and physics behaviour in ways the renderer flip does not.
- Never assume an atlas-fetched sprite is reference-equal to a scene-authored one — `SpriteAtlas.GetSprite` returns a clone per call, so comparisons fail and repeated calls allocate.
- Never ship both a Master and its Variant with Include in Build enabled — which one resolves at runtime becomes non-deterministic; disable it on the Master.
- Never claim an atlas or mesh-type change improved performance without a Profiler 2D module measurement, per `performance-and-algorithms.md`'s Verification section.
- If the requester's symptom could equally be import, material, or lighting, say which layer is being assumed and confirm before changing settings — guessing wrong here edits an asset that other scenes share.
